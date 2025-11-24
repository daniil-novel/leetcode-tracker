import paramiko
import time

def upload_and_restart():
    host = "91.84.104.36"
    user = "root"
    password = "123123123123123123123123123123Aa!"
    
    files_to_upload = [
        ("leetcode_tracker/auth.py", "/root/leetcode_tracker_uv/leetcode_tracker_uv/leetcode_tracker/auth.py"),
        ("leetcode_tracker/main.py", "/root/leetcode_tracker_uv/leetcode_tracker_uv/leetcode_tracker/main.py"),
    ]
    
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print(f"Connecting to {host}...")
        client.connect(hostname=host, username=user, password=password)
        
        sftp = client.open_sftp()
        
        print("\nUploading files with detailed logging...")
        for local_path, remote_path in files_to_upload:
            print(f"  {local_path} -> {remote_path}")
            sftp.put(local_path, remote_path)
        
        sftp.close()
        print("✅ Files uploaded successfully!")
        
        print("\nRestarting server...")
        stdin, stdout, stderr = client.exec_command("fuser -k 8000/tcp")
        time.sleep(2)
        
        cmd = "cd /root/leetcode_tracker_uv/leetcode_tracker_uv && nohup /root/.local/bin/uv run uvicorn leetcode_tracker.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &"
        client.exec_command(cmd)
        
        time.sleep(5)
        
        print("✅ Server restarted!")
        
        # Check server status
        print("\n=== Checking server status ===\n")
        stdin, stdout, stderr = client.exec_command("lsof -i :8000")
        status = stdout.read().decode()
        
        if "uvicorn" in status:
            print("✅ Server is running!\n")
            print(status)
        else:
            print("❌ Server may not be running properly")
        
        print("\n" + "=" * 60)
        print("DONE! Files uploaded and server restarted with logging")
        print("\nNow try to login and check logs with:")
        print("  python check_server_logs.py")
        print("\nOr manually:")
        print("  ssh root@91.84.104.36")
        print("  tail -50 /root/leetcode_tracker_uv/leetcode_tracker_uv/server.log")
        print("=" * 60)
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    upload_and_restart()
