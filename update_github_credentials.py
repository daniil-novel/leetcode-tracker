import paramiko

def update_env():
    host = "91.84.104.36"
    user = "root"
    password = "123123123123123123123123123123Aa!"
    
    print("=" * 60)
    print("GitHub OAuth Configuration Helper")
    print("=" * 60)
    
    print("\nPROBLEM: The current Client ID is not found on GitHub")
    print("Current Client ID: Ov23lijCFWyjFX6T5fHk")
    print("\nSOLUTION: You need to:")
    print("1. Go to https://github.com/settings/developers")
    print("2. Create a new OAuth App with these settings:")
    print("   - Application name: LeetCode Tracker")
    print("   - Homepage URL: http://v353999.hosted-by-vdsina.com:8000")
    print("   - Authorization callback URL: http://v353999.hosted-by-vdsina.com:8000/auth/callback/github")
    print("\n3. Copy the generated Client ID and Client Secret")
    print("\nOnce you have the credentials, enter them below:")
    
    client_id = input("\nEnter your GitHub Client ID: ").strip()
    client_secret = input("Enter your GitHub Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("\n❌ Error: Both Client ID and Secret are required!")
        return
    
    # Create new .env content
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
        
        print(f"\nConnecting to {host}...")
        client.connect(hostname=host, username=user, password=password)
        
        # Write .env file
        print("Updating .env file on server...")
        sftp = client.open_sftp()
        remote_file = sftp.open('/root/leetcode_tracker_uv/leetcode_tracker_uv/.env', 'w')
        remote_file.write(env_content)
        remote_file.close()
        sftp.close()
        
        print("\n✅ .env file updated successfully!")
        print("\nRestarting server...")
        
        # Restart server
        stdin, stdout, stderr = client.exec_command("fuser -k 8000/tcp")
        import time
        time.sleep(2)
        
        cmd = "cd /root/leetcode_tracker_uv/leetcode_tracker_uv && nohup /root/.local/bin/uv run uvicorn leetcode_tracker.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &"
        client.exec_command(cmd)
        
        time.sleep(5)
        
        print("\n✅ Server restarted!")
        print("\n" + "=" * 60)
        print("DONE! Now try logging in again:")
        print("http://v353999.hosted-by-vdsina.com:8000/login")
        print("=" * 60)
        
        client.close()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    update_env()
