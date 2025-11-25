import paramiko

def check_logs():
    host = "91.84.104.36"
    user = "root"
    password = "123123123123123123123123123123Aa!"
    
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print(f"Connecting to {host}...")
        client.connect(hostname=host, username=user, password=password)
        
        print("\n=== Server Logs (last 30 lines) ===\n")
        stdin, stdout, stderr = client.exec_command("tail -30 /root/leetcode_tracker_uv/leetcode_tracker_uv/server.log")
        print(stdout.read().decode())
        
        print("\n=== Server Status ===\n")
        stdin, stdout, stderr = client.exec_command("lsof -i :8000")
        print(stdout.read().decode())
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    check_logs()
