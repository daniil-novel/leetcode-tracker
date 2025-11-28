import paramiko


def verify_login():
    host = "91.84.104.36"
    user = "root"
    password = "123123123123123123123123123123Aa!"

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print(f"Connecting to {host}...")
        client.connect(hostname=host, username=user, password=password)

        # Check login.html content
        print("\n=== Checking login.html for GitHub button ===\n")
        stdin, stdout, stderr = client.exec_command(
            "grep -i 'github' /root/leetcode_tracker_uv/leetcode_tracker_uv/leetcode_tracker/templates/login.html"
        )
        content = stdout.read().decode()

        if "github" in content.lower():
            print("✅ GitHub button found in login.html!")
            print("\nMatching lines:")
            print(content[:500])
        else:
            print("❌ GitHub button NOT found in login.html")

        # Check file modification time
        print("\n=== File info ===\n")
        stdin, stdout, stderr = client.exec_command(
            "ls -lh /root/leetcode_tracker_uv/leetcode_tracker_uv/leetcode_tracker/templates/login.html"
        )
        print(stdout.read().decode())

        client.close()

    except Exception as e:
        print(f"❌ Error: {e!s}")


if __name__ == "__main__":
    verify_login()
