import paramiko
import time

def restart_server():
    host = "91.84.104.36"
    user = "root"
    password = "123123123123123123123123123123Aa!"
    
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print(f"Connecting to {host}...")
        client.connect(hostname=host, username=user, password=password)
        
        # Stop existing server
        print("Stopping existing server...")
        stdin, stdout, stderr = client.exec_command("fuser -k 8000/tcp")
        time.sleep(2)
        
        # Start server
        print("Starting server...")
        app_dir = "/root/leetcode_tracker_uv/leetcode_tracker_uv"
        cmd = f"cd {app_dir} && nohup /root/.local/bin/uv run uvicorn leetcode_tracker.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &"
        
        print(f"Executing: {cmd}")
        client.exec_command(cmd)
        
        print("Server restart command sent.")
        time.sleep(5)
        
        # Verify
        stdin, stdout, stderr = client.exec_command("lsof -i :8000")
        output = stdout.read().decode().strip()
        if output:
            print("\n✅ Server is running!")
            print(output)
        else:
            print("\n⚠️  Server might not have started. Checking logs...")
            stdin, stdout, stderr = client.exec_command(f"tail -20 {app_dir}/server.log")
            print(stdout.read().decode())
            
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    restart_server()
