import paramiko
import time

def apply_credentials():
    host = "91.84.104.36"
    user = "root"
    password = "123123123123123123123123123123Aa!"
    
    client_id = "Ov23lijCFWyjFX6T5fHk"
    client_secret = "26442ae3091e1d8663ad76908634e7b49aded6e9"
    
    env_content = f"""# JWT Secret Key (измените на случайную строку в продакшене)
SECRET_KEY=your-secret-key-change-this-to-random-string-in-production

# GitHub OAuth
# Получите на https://github.com/settings/developers
GITHUB_CLIENT_ID={client_id}
GITHUB_CLIENT_SECRET={client_secret}

# Google OAuth  
# Получите на https://console.cloud.google.com/
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here

# Database (SQLite по умолчанию)
# DATABASE_URL=sqlite:///./leetcode_tracker.db
"""
    
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print(f"Connecting to {host}...")
        client.connect(hostname=host, username=user, password=password)
        
        # Write .env file
        print("Updating .env file on server...")
        sftp = client.open_sftp()
        remote_file = sftp.open('/root/leetcode_tracker_uv/leetcode_tracker_uv/.env', 'w')
        remote_file.write(env_content)
        remote_file.close()
        sftp.close()
        
        print("✅ .env file updated successfully!")
        print("\nRestarting server...")
        
        # Restart server
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
        print("DONE! GitHub OAuth credentials updated!")
        print("\nClient ID: Ov23lijCFWyjFX6T5fHk")
        print("Client Secret: 26442...ded6e9")
        print("\nNow try logging in:")
        print("http://v353999.hosted-by-vdsina.com:8000/login")
        print("=" * 60)
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    apply_credentials()
