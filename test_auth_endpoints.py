import requests

# Test endpoints
base_url = "http://v353999.hosted-by-vdsina.com:8000"

print("=" * 60)
print("Testing LeetCode Tracker Authentication Endpoints")
print("=" * 60)

# Test 1: Check if server is running
print("\n1. Testing main page...")
try:
    response = requests.get(base_url, timeout=5)
    print(f"   ✅ Main page: {response.status_code}")
except Exception as e:
    print(f"   ❌ Main page failed: {e}")

# Test 2: Check login page
print("\n2. Testing login page...")
try:
    response = requests.get(f"{base_url}/login", timeout=5)
    print(f"   ✅ Login page: {response.status_code}")
    if response.status_code == 200:
        if "GitHub" in response.text:
            print("   ✅ GitHub auth button found")
        else:
            print("   ⚠️  GitHub auth button not found in page")
except Exception as e:
    print(f"   ❌ Login page failed: {e}")

# Test 3: Check GitHub auth redirect
print("\n3. Testing GitHub OAuth redirect...")
try:
    response = requests.get(f"{base_url}/auth/github", allow_redirects=False, timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 307 or response.status_code == 302:
        redirect_url = response.headers.get('Location', '')
        print(f"   ✅ Redirects to: {redirect_url[:100]}...")
        if "github.com" in redirect_url:
            print("   ✅ Redirects to GitHub OAuth")
        else:
            print("   ⚠️  Does not redirect to GitHub")
    else:
        print(f"   ❌ Expected redirect (302/307), got {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ GitHub auth redirect failed: {e}")

# Test 4: Check if API is accessible
print("\n4. Testing API endpoint...")
try:
    response = requests.get(f"{base_url}/docs", timeout=5)
    print(f"   ✅ API docs: {response.status_code}")
except Exception as e:
    print(f"   ❌ API docs failed: {e}")

print("\n" + "=" * 60)
print("Test completed!")
print("=" * 60)
