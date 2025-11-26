# LeetCode Username Connection Troubleshooting Guide

## Understanding LeetCode Username Format

### Common Problems and Solutions

#### 1. **Username Format**
The username you enter should match EXACTLY what appears in your LeetCode profile URL.

**How to find your correct username:**
1. Go to https://leetcode.com and log in
2. Click on your profile picture in the top right
3. Look at the URL in your browser's address bar
4. The format will be: `https://leetcode.com/u/YOUR_USERNAME/`
5. Copy only the `YOUR_USERNAME` part (without the `/u/` prefix or trailing `/`)

**Examples:**
- ✅ Correct: `user0934Nf` (if URL is `leetcode.com/u/user0934Nf/`)
- ✅ Correct: `john_doe` (if URL is `leetcode.com/u/john_doe/`)
- ✅ Correct: `Daniil-novel` (if URL is `leetcode.com/u/Daniil-novel/`)
- ❌ Wrong: `/u/user0934Nf/`
- ❌ Wrong: `https://leetcode.com/u/user0934Nf/`

#### 2. **Profile Privacy Settings**
Your LeetCode profile MUST be set to **Public** for the integration to work.

**How to make your profile public:**
1. Go to https://leetcode.com
2. Click on your profile picture → Settings
3. Find "Profile Visibility" or "Privacy Settings"
4. Set your profile to **Public**
5. Save changes

#### 3. **Username Case Sensitivity**
LeetCode usernames are case-sensitive. Make sure you enter it exactly as it appears in the URL.

- If your URL is `leetcode.com/u/user0934Nf/`, enter: `user0934Nf`
- If your URL is `leetcode.com/u/Daniil-novel/`, enter: `Daniil-novel`

#### 4. **Special Characters**
LeetCode usernames can contain:
- Letters (a-z, A-Z)
- Numbers (0-9)
- Hyphens (-)
- Underscores (_)

Usernames like "user0934Nf" or "Daniil-novel" are valid if that's exactly how they appear in your profile URL.

## Testing Your Username

### Method 1: Direct Browser Test
1. Open a new browser tab (use incognito/private mode to test as if you're not logged in)
2. Go to: `https://leetcode.com/u/YOUR_USERNAME/`
3. Replace `YOUR_USERNAME` with your actual username (e.g., `user0934Nf`)
4. If you see a profile page with statistics, your username is correct and public
5. If you see "User not found" or are redirected, the username is wrong or the profile is private

### Method 2: Test in the Application
1. Log into the LeetCode Tracker application
2. Go to Profile Settings
3. Enter your username exactly as it appears in the LeetCode URL
4. Click "Connect LeetCode"
5. Wait for the response:
   - ✅ Success: "LeetCode username updated successfully!"
   - ❌ Error: "LeetCode user 'YOUR_USERNAME' not found..."

## Common Error Messages and Solutions

### Error: "LeetCode user 'YOUR_USERNAME' not found"
**Possible causes:**
1. Username is incorrect (typo, wrong case, etc.)
2. Profile is set to Private
3. The account doesn't exist on LeetCode

**Solutions:**
1. Double-check the username in your LeetCode profile URL
2. Verify your profile is set to Public in LeetCode settings
3. Try accessing `https://leetcode.com/u/YOUR_USERNAME/` in an incognito browser (replace YOUR_USERNAME with your actual username)

### Error: "Please check the username and make sure your profile is public"
**This means:**
- The system couldn't fetch your profile data from LeetCode
- Most likely your profile is set to Private

**Solution:**
1. Go to LeetCode Settings
2. Change Profile Visibility to Public
3. Wait a few minutes for changes to take effect
4. Try connecting again

### Error: "Network error. Please try again."
**Possible causes:**
1. Internet connection issue
2. LeetCode API is temporarily unavailable
3. Server connection problem

**Solutions:**
1. Check your internet connection
2. Wait a few minutes and try again
3. Try refreshing the page

## Important Clarification

**Note:** "user0934Nf" is actually a valid LeetCode username (not a password or user ID).

- ✅ If your profile URL is `https://leetcode.com/u/user0934Nf/`, then "user0934Nf" IS your username
- ❌ You do NOT need your LeetCode password
- ❌ You do NOT need any authentication tokens
- ✅ You ONLY need your public LeetCode username (which could be "user0934Nf")

The integration works by:
1. Fetching publicly available data from your LeetCode profile
2. Using LeetCode's public GraphQL API
3. No authentication with LeetCode is required
4. Your LeetCode Tracker account is separate from your LeetCode account

## Step-by-Step Connection Guide

### Step-by-Step Example (using "user0934Nf"):

1. **Verify your LeetCode username:**
   ```
   - Go to: https://leetcode.com
   - Log in to your account
   - Click your profile picture
   - Check the URL: https://leetcode.com/u/???/
   - The ??? is your username
   ```

2. **Make profile public:**
   ```
   - Go to LeetCode Settings
   - Find "Profile Visibility"
   - Select "Public"
   - Save
   ```

3. **Test in incognito:**
   ```
   - Open incognito/private browser
   - Go to: https://leetcode.com/u/user0934Nf/
   - Can you see the profile? 
     - YES → Username is correct and public ✅
     - NO → Username is wrong or profile is private ❌
   ```

4. **Connect in LeetCode Tracker:**
   ```
   - Go to Profile Settings
   - Enter: user0934Nf (exactly as in URL)
   - Click "Connect LeetCode"
   - Wait for confirmation
   ```

## Still Having Issues?

If you've tried all the above and still can't connect:

1. **Check the exact URL format:**
   - Old format: `leetcode.com/Daniil-novel/` (without `/u/`)
   - New format: `leetcode.com/u/Daniil-novel/` (with `/u/`)
   - Both should work, but use the username part only

2. **Try different variations (case-sensitive):**
   - Check the exact case: `user0934Nf` vs `User0934Nf` vs `user0934nf`
   - Whatever matches your actual LeetCode profile URL exactly

3. **Verify account exists:**
   - Make sure you actually have a LeetCode account
   - Make sure you've solved at least one problem (for statistics to appear)

4. **Check browser console:**
   - Open browser Developer Tools (F12)
   - Go to Console tab
   - Try connecting
   - Look for any error messages
   - Share these with support if needed

## Summary

✅ **What you need:**
- Your LeetCode username (from the profile URL)
- Profile set to Public

❌ **What you DON'T need:**
- LeetCode password
- User ID like "user0934Nf"
- Any authentication tokens

Usernames like "user0934Nf" are valid IF that's exactly how they appear in your LeetCode profile URL. The most common issue is that the profile is set to Private.
