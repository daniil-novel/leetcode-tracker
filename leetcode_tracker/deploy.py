import logging
from pathlib import Path, PurePosixPath
import subprocess
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


def build_frontend():
    """Build frontend application locally."""
    logger.info("🏗️ Building frontend...")
    frontend_dir = Path.cwd() / "frontend"

    if not frontend_dir.exists():
        logger.error(f"❌ Frontend directory not found at {frontend_dir}")
        sys.exit(1)

    # Check if npm is available
    try:
        subprocess.run(["npm", "--version"], check=True, capture_output=True, shell=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("❌ npm is not installed or not in PATH")
        sys.exit(1)

    try:
        # Install dependencies
        logger.info("Installing frontend dependencies...")
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True, shell=True)

        # Build
        logger.info("Building frontend...")
        subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True, shell=True)
        logger.info("✅ Frontend built successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Frontend build failed: {e}")
        sys.exit(1)


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

    # 0. Build frontend locally
    build_frontend()

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

        # 5.5 Update Nginx config
        execute_command(
            client, f"cp {REMOTE_DIR}/nginx-leetcode-tracker.conf /etc/nginx/sites-available/novel-cloudtech.com", "Updating Nginx config"
        )
        # Ensure symlink exists (just in case)
        execute_command(
            client, "ln -sf /etc/nginx/sites-available/novel-cloudtech.com /etc/nginx/sites-enabled/", "Ensuring Nginx symlink"
        )
        execute_command(client, "nginx -t && systemctl reload nginx", "Reloading Nginx")

        # 6. Start service
        execute_command(client, "systemctl start leetcode-tracker", "Starting service")

        # 6.5 Start Grafana
        logger.info("📊 Starting Grafana...")
        # Ensure DB is readable by Grafana
        execute_command(client, f"chmod 644 {REMOTE_DIR}/leetcode.db", "Setting DB permissions")

        # Use docker run directly to avoid docker-compose version issues
        logger.info("▶️  Recreating Grafana container...")
        execute_command(client, "docker rm -f leetcode_grafana", "Removing old container")
        execute_command(client, "docker volume create grafana_data", "Creating volume")
        
        grafana_cmd = (
            "docker run -d "
            "--name leetcode_grafana "
            "--user 0 "
            "-p 3000:3000 "
            "-v grafana_data:/var/lib/grafana "
            f"-v {REMOTE_DIR}/leetcode.db:/data/leetcode.db:ro "
            f"-v {REMOTE_DIR}/grafana/provisioning:/etc/grafana/provisioning "
            "-e GF_INSTALL_PLUGINS=fr-ser-sqlite-datasource "
            "-e GF_SECURITY_ADMIN_PASSWORD=admin "
            "-e GF_USERS_ALLOW_SIGN_UP=false "
            "-e GF_SERVER_ROOT_URL='https://novel-cloudtech.com:7443/grafana/' "
            "-e GF_SERVER_SERVE_FROM_SUB_PATH=true "
            "-e GF_SECURITY_ALLOW_EMBEDDING=true "
            "-e GF_AUTH_ANONYMOUS_ENABLED=true "
            "-e GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer "
            "--restart unless-stopped "
            "grafana/grafana:latest"
        )
        
        execute_command(client, grafana_cmd, "Starting Grafana container")

        # 7. check status
        time.sleep(5)
        execute_command(client, "docker ps | grep leetcode_grafana", "Checking Grafana container status")
        execute_command(client, "docker logs --tail 20 leetcode_grafana", "Grafana Logs")
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
