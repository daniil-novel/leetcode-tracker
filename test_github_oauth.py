import paramiko

def test_oauth():
    host = "91.84.104.36"
    user = "root"
    password = "123123123123123123123123123123Aa!"
    
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print(f"Connecting to {host}...")
        client.connect(hostname=host, username=user, password=password)
        
        # Test GitHub OAuth endpoint
        print("\n=== Testing GitHub OAuth endpoint ===\n")
        stdin, stdout, stderr = client.exec_command("curl -I http://localhost:8000/auth/github 2>&1 | head -20")
        print(stdout.read().decode())
        
        # Check .env values
        print("\n=== Checking .env GitHub credentials ===\n")
        stdin, stdout, stderr = client.exec_command("grep GITHUB /root/leetcode_tracker_uv/leetcode_tracker_uv/.env")
        print(stdout.read().decode())
        
        # Check if authlib is installed
        print("\n=== Checking authlib installation ===\n")
        stdin, stdout, stderr = client.exec_command("cd /root/leetcode_tracker_uv/leetcode_tracker_uv && /root/.local/bin/uv pip list | grep authlib")
        print(stdout.read().decode())
        
        # Check recent logs for errors
        print("\n=== Recent error logs ===\n")
        stdin, stdout, stderr = client.exec_command("tail -50 /root/leetcode_tracker_uv/leetcode_tracker_uv/server.log | grep -i error")
        errors = stdout.read().decode()
        if errors:
            print(errors)
        else:
            print("No errors found in logs")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_oauth()
