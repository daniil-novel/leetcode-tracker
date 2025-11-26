import os
import sys
import time
import logging
import paramiko
from pathlib import Path
from stat import S_ISDIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
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
    ".env",           # Don't overwrite production secrets
    "leetcode.db",    # Don't overwrite production database
    "scripts",        # We are running from here, but maybe useful to have on server? Let's keep it.
    "auto_deploy.py", # Deleted locally, but just in case
    "deploy_to_server.sh",
    "node_modules"    # Exclude node_modules from frontend
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

def execute_command(client, command, description=None):
    """Execute command on server and log output."""
    if description:
        logger.info(f"▶️  {description}")
    else:
        logger.info(f"Running: {command}")

    stdin, stdout, stderr = client.exec_command(command)
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

def upload_files(sftp, local_path, remote_path):
    """Recursively upload files."""
    local_path = Path(local_path)
    remote_path = str(remote_path).replace("\\", "/")

    # Create remote directory if it doesn't exist
    try:
        sftp.stat(remote_path)
    except IOError:
        try:
            sftp.mkdir(remote_path)
            logger.info(f"Created remote directory: {remote_path}")
        except IOError as e:
            logger.error(f"Failed to create remote directory {remote_path}: {e}")
            return

    for item in os.listdir(local_path):
        if item in EXCLUDE_LIST or item.endswith(".pyc") or item.endswith(".DS_Store"):
            continue

        local_item_path = local_path / item
        remote_item_path = f"{remote_path}/{item}"

        if local_item_path.is_dir():
            upload_files(sftp, local_item_path, remote_item_path)
        else:
            try:
                sftp.put(str(local_item_path), remote_item_path)
                logger.debug(f"Uploaded: {item}")
            except Exception as e:
                logger.error(f"Failed to upload {item}: {e}")

def main():
    start_time = time.time()
    logger.info("🚀 Starting deployment...")

    client = create_ssh_client()
    sftp = client.open_sftp()

    try:
        # 1. Stop service
        execute_command(client, "systemctl stop leetcode-tracker", "Stopping service")

        # 2. Upload files
        logger.info("📦 Uploading files...")
        upload_files(sftp, Path.cwd(), REMOTE_DIR)
        logger.info("✅ Files uploaded")

        # 3. Update dependencies
        execute_command(client, f"cd {REMOTE_DIR} && /root/.local/bin/uv sync", "Syncing dependencies with UV")

        # 4. Update systemd service if changed
        execute_command(client, f"cp {REMOTE_DIR}/leetcode-tracker.service /etc/systemd/system/", "Updating systemd service")
        execute_command(client, "systemctl daemon-reload", "Reloading systemd daemon")

        # 5. Start service
        execute_command(client, "systemctl start leetcode-tracker", "Starting service")
        
        # 6. check status
        time.sleep(2)
        execute_command(client, "systemctl status leetcode-tracker --no-pager", "Checking service status")

        duration = time.time() - start_time
        logger.info(f"✨ Deployment completed in {duration:.2f} seconds")
        logger.info(f"🌐 Home page: https://novel-cloudtech.com:7443")

    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
    finally:
        sftp.close()
        client.close()

if __name__ == "__main__":
    main()
