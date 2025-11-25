import paramiko
import os

def upload_templates():
    host = "91.84.104.36"
    user = "root"
    password = "123123123123123123123123123123Aa!"
    
    try:
        # Establish SSH connection
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print(f"Connecting to {host}...")
        client.connect(hostname=host, username=user, password=password)
        
        # Setup SFTP
        sftp = client.open_sftp()
        
        # Upload templates
        templates = [
            'leetcode_tracker/templates/login.html',
            'leetcode_tracker/templates/base.html',
            'leetcode_tracker/templates/index.html'
        ]
        
        remote_dir = '/root/leetcode_tracker_uv/leetcode_tracker_uv/leetcode_tracker/templates/'
        
        for template in templates:
            if os.path.exists(template):
                remote_path = remote_dir + os.path.basename(template)
                print(f"Uploading {template} to {remote_path}...")
                sftp.put(template, remote_path)
                print(f"✅ Uploaded {template}")
            else:
                print(f"❌ File not found: {template}")
        
        # Also upload auth.py, main.py, models.py, schemas.py
        python_files = [
            'leetcode_tracker/auth.py',
            'leetcode_tracker/main.py',
            'leetcode_tracker/models.py',
            'leetcode_tracker/schemas.py'
        ]
        
        remote_py_dir = '/root/leetcode_tracker_uv/leetcode_tracker_uv/leetcode_tracker/'
        
        for py_file in python_files:
            if os.path.exists(py_file):
                remote_path = remote_py_dir + os.path.basename(py_file)
                print(f"Uploading {py_file} to {remote_path}...")
                sftp.put(py_file, remote_path)
                print(f"✅ Uploaded {py_file}")
            else:
                print(f"❌ File not found: {py_file}")
        
        sftp.close()
        client.close()
        
        print("\n" + "="*60)
        print("✅ All files uploaded successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    upload_templates()
