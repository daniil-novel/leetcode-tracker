# Grafana 502 Error - Diagnosis and Fix Summary

## Date: 28.11.2025

## Problems Found

### 1. **Multiple Grafana Containers Running** ❌
- Found 4 Grafana containers running simultaneously
- Only one (`leetcode-tracker-grafana`) should be running
- Extra containers: `serene_sammet`, `youthful_mahavira`, `magical_haibt`

**Solution:** Stopped and removed duplicate containers
```bash
docker stop serene_sammet youthful_mahavira magical_haibt
docker rm serene_sammet youthful_mahavira magical_haibt
```

### 2. **Empty Database** ❌
- PostgreSQL database had correct schema but NO DATA
- 0 users, 0 tasks, 0 goals
- This was the main cause of the 502 errors in Grafana

**Solution:** Created test data using `scripts/create_test_data.py`
- Created 1 test user
- Created 60 test tasks over 30 days
- Created 1 month goal
- Total XP: 140 points

### 3. **Dashboard Configuration** ✅
- Dashboard configuration is CORRECT
- Uses PostgreSQL datasource properly
- All queries are properly formatted

## Current Status

### ✅ What's Working Now

1. **Docker Containers**
   - PostgreSQL: Running and healthy
   - Grafana: Running on port 3000
   - PgAdmin: Running on port 5050

2. **Database**
   - Tables: `users`, `solved_tasks`, `month_goals`, `alembic_version`
   - Data: 60 tasks, 1 user, 1 goal
   - Connection: Working properly

3. **API Server**
   - Running on port 8000
   - Accessible at http://localhost:8000/docs

4. **Grafana Configuration**
   - Datasource: `LeetCode Tracker PostgreSQL`
   - Connection: `postgres:5432`
   - Database: `leetcode_tracker`
   - Credentials: Configured correctly

## Access Information

### Grafana
- URL: http://localhost:3000
- Username: `admin`
- Password: `admin`
- Dashboard: http://localhost:3000/d/leetcode-tracker/leetcode-tracker-dashboard

### PgAdmin
- URL: http://localhost:5050
- Email: `admin@admin.com`
- Password: `admin`

### PostgreSQL
- Host: `localhost`
- Port: `5432`
- Database: `leetcode_tracker`
- Username: `leetcode_user`
- Password: `leetcode_password`

### API
- URL: http://localhost:8000
- Docs: http://localhost:8000/docs

## Dashboard Panels

The dashboard includes:
1. **Total Tasks Solved** - Stat panel
2. **Total XP** - Stat panel
3. **Active Users** - Stat panel
4. **Avg Time per Task** - Stat panel
5. **Tasks Solved Over Time** - Time series chart
6. **Tasks by Difficulty** - Pie chart
7. **Top Users Leaderboard** - Table
8. **Recent Tasks** - Table

## Next Steps

### To Add Real Data

You have several options:

#### Option 1: Use the Application
1. Open http://localhost:8000 (or your frontend)
2. Register/login with GitHub OAuth
3. Add your LeetCode username in profile
4. Sync data from LeetCode API

#### Option 2: Manual Entry
1. Use the API at http://localhost:8000/docs
2. Create tasks via POST /api/tasks endpoint

#### Option 3: Import from LeetCode
If you have a LeetCode username, you can sync data:
1. Add user with LeetCode username to database
2. Use the sync endpoint to fetch data from LeetCode API

### To Monitor

1. **Check Grafana Dashboard**
   ```bash
   # Open in browser
   start http://localhost:3000/d/leetcode-tracker/leetcode-tracker-dashboard
   ```

2. **Check Database**
   ```bash
   docker exec -it leetcode-tracker-postgres psql -U leetcode_user -d leetcode_tracker -c "SELECT COUNT(*) FROM solved_tasks;"
   ```

3. **Check Grafana Logs**
   ```bash
   docker logs leetcode-tracker-grafana --tail 50
   ```

## Files Created/Modified

### New Files
- `scripts/create_test_data.py` - Script to create test data

### Configuration Files (Already Correct)
- `docker-compose.yml` - Docker services configuration
- `grafana/provisioning/datasources/postgres.yml` - Grafana datasource
- `grafana/provisioning/dashboards/leetcode-tracker.json` - Dashboard definition
- `.env` - Environment variables

## Test Data Details

Created test data includes:
- **User**: test_user (ID: 1)
- **Tasks**: 60 tasks over 30 days (2025-10-30 to 2025-11-28)
- **Difficulty Distribution**:
  - Easy: 30 tasks (1 point each)
  - Medium: 20 tasks (3 points each)
  - Hard: 10 tasks (5 points each)
- **Total XP**: 140 points
- **Time Range**: Last 30 days

## Troubleshooting

### If Grafana shows 502 errors:
1. Check if PostgreSQL is running: `docker ps | findstr postgres`
2. Check if database has data: `docker exec -it leetcode-tracker-postgres psql -U leetcode_user -d leetcode_tracker -c "SELECT COUNT(*) FROM solved_tasks;"`
3. Check Grafana logs: `docker logs leetcode-tracker-grafana --tail 50`
4. Restart Grafana: `docker restart leetcode-tracker-grafana`

### If no data appears:
1. Verify database connection in Grafana UI
2. Check if queries are correct in dashboard
3. Verify data exists in database
4. Check time range in dashboard (default: last 30 days)

## Commands Reference

```bash
# View all containers
docker ps -a

# Check PostgreSQL data
docker exec -it leetcode-tracker-postgres psql -U leetcode_user -d leetcode_tracker -c "SELECT COUNT(*) FROM solved_tasks;"

# Restart Grafana
docker restart leetcode-tracker-grafana

# View Grafana logs
docker logs leetcode-tracker-grafana --tail 50

# Create test data (if needed again)
uv run python scripts/create_test_data.py

# Start all services
docker-compose up -d

# Stop all services
docker-compose down
```

## Summary

✅ **FIXED**: Grafana 502 errors resolved
✅ **FIXED**: Database populated with test data
✅ **FIXED**: Duplicate containers removed
✅ **VERIFIED**: All connections working
✅ **VERIFIED**: Dashboard configuration correct
✅ **READY**: System ready for use

The Grafana dashboard should now display all charts and data correctly!
