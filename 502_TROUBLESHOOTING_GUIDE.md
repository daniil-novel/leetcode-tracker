# 502 Bad Gateway Troubleshooting Guide

## Problem
Getting "502 Bad Gateway nginx/1.18.0 (Ubuntu)" error after removing code from the project.

## Most Common Causes

### 1. **Missing Dependencies**
When you removed code, you might have also removed some dependencies from `pyproject.toml` that are still needed.

**Solution:**
```bash
cd /root/leetcode_tracker_uv
uv sync
```

### 2. **Application Not Running**
The FastAPI application on port 8000 might not be running.

**Check:**
```bash
systemctl status leetcode-tracker
journalctl -u leetcode-tracker -n 50
```

**Fix:**
```bash
systemctl restart leetcode-tracker
```

### 3. **Missing .env File**
The application requires environment variables to start.

**Required variables in `.env`:**
- `SECRET_KEY` - Required for JWT tokens
- `GITHUB_CLIENT_ID` - Required for OAuth
- `GITHUB_CLIENT_SECRET` - Required for OAuth

**Check:**
```bash
cat /root/leetcode_tracker_uv/.env
```

### 4. **Import Errors**
You might have deleted a file that's still being imported somewhere.

**Check logs for import errors:**
```bash
journalctl -u leetcode-tracker -n 100 | grep -i "import\|error\|exception"
```

### 5. **Missing Frontend Build**
The application tries to serve frontend files from `frontend/dist`.

**Check:**
```bash
ls -la /root/leetcode_tracker_uv/frontend/dist/
```

**Rebuild if missing:**
```bash
cd /root/leetcode_tracker_uv/frontend
npm install
npm run build
```

## Quick Diagnostic Steps

### Step 1: Run the diagnostic script
```bash
cd /root/leetcode_tracker_uv
chmod +x diagnose_502.sh
./diagnose_502.sh
```

This will check:
- Service status
- Service logs
- Port 8000 listening
- Nginx status
- .env file
- Frontend build
- Dependencies

### Step 2: Run the fix script
```bash
cd /root/leetcode_tracker_uv
chmod +x fix_502_error.sh
./fix_502_error.sh
```

This will:
- Stop the service
- Sync dependencies
- Check .env file
- Check frontend build
- Test application startup
- Restart the service

## Manual Troubleshooting

### Test the application manually
```bash
cd /root/leetcode_tracker_uv
uv run uvicorn leetcode_tracker.main:app --host 127.0.0.1 --port 8001
```

This will show you the exact error if the app fails to start.

### Check what was deleted
```bash
git status
git diff HEAD
```

### Restore deleted files if needed
```bash
git checkout HEAD -- <filename>
```

## Common Error Messages and Solutions

### "ModuleNotFoundError: No module named 'X'"
**Cause:** You deleted a module that's still imported somewhere.

**Solution:** Either restore the module or remove the import.

### "ValidationError" from Pydantic
**Cause:** Missing required environment variables in `.env`.

**Solution:** Add the missing variables to `.env` file.

### "No such file or directory: 'frontend/dist'"
**Cause:** Frontend not built.

**Solution:**
```bash
cd /root/leetcode_tracker_uv/frontend
npm run build
```

### Port 8000 not listening
**Cause:** Application failed to start.

**Solution:** Check logs with `journalctl -u leetcode-tracker -n 100`

## Recovery Steps

If you're not sure what you deleted:

1. **Check git history:**
   ```bash
   git log --oneline -10
   git show HEAD
   ```

2. **See what changed:**
   ```bash
   git diff HEAD~1 HEAD
   ```

3. **Restore everything to last commit:**
   ```bash
   git reset --hard HEAD
   ```

4. **Or restore specific file:**
   ```bash
   git checkout HEAD -- <filename>
   ```

## Prevention

Before deleting code in the future:

1. **Create a git commit first:**
   ```bash
   git add .
   git commit -m "Before cleanup"
   ```

2. **Test locally before deploying:**
   ```bash
   uv run uvicorn leetcode_tracker.main:app --reload
   ```

3. **Check for unused imports:**
   ```bash
   ruff check --select F401
   ```

## Still Not Working?

Run this command and share the output:
```bash
cd /root/leetcode_tracker_uv
./diagnose_502.sh > diagnostic_output.txt 2>&1
cat diagnostic_output.txt
```

This will help identify the exact issue.
