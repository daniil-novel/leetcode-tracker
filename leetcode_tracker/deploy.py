import logging
from pathlib import Path, PurePosixPath
import sys
import time

import paramiko


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("deploy")

# Server configuration
SERVER_HOST = "v353999.hosted-by-vdsina.com"
SERVER_PORT = 22
SERVER_USER = "root"
SERVER_PASS = "123123123123123123123123123123Aa!"
REMOTE_DIR = "/root/leetcode_tracker_uv"

# Files/Directories to exclude from upload
EXCLUDE_LIST = {
    ".git",
    ".venv",
    "__pycache__",
    ".env",  # Don't overwrite production secrets
    "leetcode.db",  # Don't overwrite production database
    "scripts",  # We are running from here, but maybe useful to have on server? Let's keep it.
    "auto_deploy.py",  # Deleted locally, but just in case
    "deploy_to_server.sh",
    "node_modules",  # Exclude node_modules from frontend
}


def create_ssh_client():
    """Create and connect SSH client."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logger.info(f"Connecting to {SERVER_HOST}...")
        client.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASS)
        logger.info("✅ Connected successfully")
        return client
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        sys.exit(1)


def execute_command(client, command, description=None) -> bool:
    """Execute command on server and log output."""
    if description:
        logger.info(f"▶️  {description}")
    else:
        logger.info(f"Running: {command}")

    _stdin, stdout, stderr = client.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()

    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()

    if out:
        logger.info(f"STDOUT: {out}")
    if err:
        logger.warning(f"STDERR: {err}")

    if exit_status != 0:
        logger.error(f"❌ Command failed with status {exit_status}")
        return False
    return True


def mkdir_p(sftp, remote_directory) -> None:
    """Create remote directory recursively (like mkdir -p)."""
    remote_directory = str(remote_directory).replace("\\", "/")

    if remote_directory == "/":
        return

    try:
        sftp.stat(remote_directory)
    except OSError:
        # Directory doesn't exist, create parent first
        parent = str(PurePosixPath(remote_directory).parent)
        if parent and parent != remote_directory:
            mkdir_p(sftp, parent)

        try:
            sftp.mkdir(remote_directory)
            logger.debug(f"Created remote directory: {remote_directory}")
        except OSError as e:
            # Directory might have been created by another process
            try:
                sftp.stat(remote_directory)
            except OSError:
                logger.error(f"Failed to create remote directory {remote_directory}: {e}")
                raise


def upload_files(sftp, local_path, remote_path) -> None:
    """Recursively upload files."""
    local_path = Path(local_path)
    remote_path = str(remote_path).replace("\\", "/")

    # Create remote directory if it doesn't exist (recursively)
    mkdir_p(sftp, remote_path)

    for item in local_path.iterdir():
        if item.name in EXCLUDE_LIST or item.name.endswith((".pyc", ".DS_Store")):
            continue

        local_item_path = item
        remote_item_path = f"{remote_path}/{item.name}"

        if local_item_path.is_dir():
            upload_files(sftp, local_item_path, remote_item_path)
        else:
            try:
                sftp.put(str(local_item_path), remote_item_path)
                logger.debug(f"Uploaded: {item.name}")
            except Exception as e:
                logger.error(f"Failed to upload {item.name}: {e}")


def main() -> None:
    start_time = time.time()
    logger.info("🚀 Starting deployment...")

    client = create_ssh_client()
    sftp = client.open_sftp()

    try:
        # 1. Stop service
        execute_command(client, "systemctl stop leetcode-tracker", "Stopping service")

        # 1.5 Clean up obsolete files
        logger.info("🧹 Cleaning up obsolete files...")
        execute_command(client, f"rm -f {REMOTE_DIR}/leetcode_tracker/routers/frontend.py", "Removing frontend.py")
        execute_command(client, f"rm -rf {REMOTE_DIR}/leetcode_tracker/templates", "Removing templates directory")
        execute_command(client, f"rm -rf {REMOTE_DIR}/leetcode_tracker/static", "Removing static directory")

        # 2. Upload files
        logger.info("📦 Uploading files...")
        upload_files(sftp, Path.cwd(), REMOTE_DIR)
        logger.info("✅ Files uploaded")

        # 3. Update dependencies
        execute_command(client, f"cd {REMOTE_DIR} && /root/.local/bin/uv sync", "Syncing dependencies with UV")

        # 4. Apply database migrations
        execute_command(
            client, f"cd {REMOTE_DIR} && /root/.local/bin/uv run alembic upgrade head", "Applying database migrations"
        )

        # 5. Update systemd service if changed
        execute_command(
            client, f"cp {REMOTE_DIR}/leetcode-tracker.service /etc/systemd/system/", "Updating systemd service"
        )
        execute_command(client, "systemctl daemon-reload", "Reloading systemd daemon")

        # 6. Start service
        execute_command(client, "systemctl start leetcode-tracker", "Starting service")

        # 7. check status
        time.sleep(2)
        execute_command(client, "systemctl status leetcode-tracker --no-pager", "Checking service status")

        duration = time.time() - start_time
        logger.info(f"✨ Deployment completed in {duration:.2f} seconds")
        logger.info("🌐 Home page: https://novel-cloudtech.com:7443")

    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
    finally:
        sftp.close()
        client.close()


if __name__ == "__main__":
    main()
