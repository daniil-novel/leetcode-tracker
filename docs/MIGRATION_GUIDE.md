# SQLite to PostgreSQL Migration Guide

This guide will help you migrate your LeetCode Tracker database from SQLite to PostgreSQL.

## Overview

The migration process involves:
1. Installing PostgreSQL dependencies
2. Starting PostgreSQL with Docker Compose
3. Running the migration script to transfer data
4. Updating your application configuration
5. Verifying the migration

## Prerequisites

- Docker and Docker Compose installed
- Existing SQLite database (`leetcode.db`)
- Python environment with uv

## Step-by-Step Migration

### 1. Install Dependencies

First, install the PostgreSQL driver:

```bash
uv sync
```

This will install `psycopg2-binary` which is required for PostgreSQL connections.

### 2. Start PostgreSQL Container

Start the PostgreSQL database using Docker Compose:

```bash
docker-compose up -d postgres
```

Wait for PostgreSQL to be ready (about 10-15 seconds). You can check the status:

```bash
docker-compose ps
```

### 3. Backup Your SQLite Database (Optional but Recommended)

Before migrating, create a backup of your SQLite database:

```bash
cp leetcode.db leetcode.db.backup
```

### 4. Run the Migration Script

Execute the migration script to transfer data from SQLite to PostgreSQL:

```bash
python scripts/migrate_sqlite_to_postgres.py
```

The script will:
- Export all data from SQLite (users, solved tasks, month goals)
- Create a JSON backup file (`migration_backup.json`)
- Create tables in PostgreSQL
- Import all data to PostgreSQL
- Update PostgreSQL sequences

When prompted, type `yes` to confirm the migration.

### 5. Verify the Migration

Check that the data was migrated successfully by connecting to PostgreSQL:

```bash
docker exec -it leetcode-tracker-postgres psql -U leetcode_user -d leetcode_tracker
```

Then run some queries:

```sql
-- Check users
SELECT COUNT(*) FROM users;

-- Check solved tasks
SELECT COUNT(*) FROM solved_tasks;

-- Check month goals
SELECT COUNT(*) FROM month_goals;

-- Exit psql
\q
```

### 6. Update Application Configuration

The `.env` file has already been updated to use PostgreSQL. Verify the configuration:

```env
DATABASE_URL=postgresql://leetcode_user:leetcode_password@localhost:5432/leetcode_tracker
```

### 7. Run Database Migrations (if needed)

If you have any pending Alembic migrations, run them:

```bash
alembic upgrade head
```

### 8. Start Your Application

Start your FastAPI application using uv:

```bash
uv run uvicorn leetcode_tracker.main:app --reload
```

Test that everything works correctly by:
- Logging in
- Viewing your dashboard
- Adding a new task
- Checking statistics

### 9. Start Grafana (Optional)

If you use Grafana for analytics, start it with the updated PostgreSQL datasource:

```bash
docker-compose up -d grafana
```

Access Grafana at http://localhost:3000 (admin/admin) and verify that the dashboards work with PostgreSQL.

## Configuration Details

### Database Connection String

The PostgreSQL connection string format:
```
postgresql://username:password@host:port/database
```

Default configuration:
- **Username**: `leetcode_user`
- **Password**: `leetcode_password`
- **Host**: `localhost` (or `postgres` inside Docker network)
- **Port**: `5432`
- **Database**: `leetcode_tracker`

### Environment Variables

Key environment variables in `.env`:

```env
# PostgreSQL connection for the application
DATABASE_URL=postgresql://leetcode_user:leetcode_password@localhost:5432/leetcode_tracker

# PostgreSQL credentials (used by Docker Compose)
POSTGRES_USER=leetcode_user
POSTGRES_PASSWORD=leetcode_password
POSTGRES_DB=leetcode_tracker
```

## Troubleshooting

### PostgreSQL Container Won't Start

Check if port 5432 is already in use:
```bash
netstat -an | findstr 5432
```

If another PostgreSQL instance is running, either stop it or change the port in `docker-compose.yml`.

### Migration Script Fails

1. Ensure PostgreSQL is running:
   ```bash
   docker-compose ps postgres
   ```

2. Check PostgreSQL logs:
   ```bash
   docker-compose logs postgres
   ```

3. Verify the SQLite database exists:
   ```bash
   ls -la leetcode.db
   ```

### Connection Errors

If you get connection errors:

1. Check that PostgreSQL is accessible:
   ```bash
   docker exec -it leetcode-tracker-postgres pg_isready
   ```

2. Verify credentials in `.env` match those in `docker-compose.yml`

3. Ensure the DATABASE_URL is correct

### Data Not Showing Up

1. Check that the migration completed successfully
2. Verify data exists in PostgreSQL (see Step 5)
3. Check application logs for errors
4. Ensure you're using the correct DATABASE_URL

## Rollback to SQLite

If you need to rollback to SQLite:

1. Stop the application

2. Update `.env`:
   ```env
   DATABASE_URL=sqlite:///./leetcode.db
   ```

3. Restore your backup (if you made one):
   ```bash
   cp leetcode.db.backup leetcode.db
   ```

4. Restart the application

## Performance Considerations

PostgreSQL offers several advantages over SQLite:

- **Better concurrency**: Multiple users can write simultaneously
- **Advanced features**: Better indexing, full-text search, JSON support
- **Scalability**: Handles larger datasets more efficiently
- **Production-ready**: Suitable for deployment in production environments

## Security Notes

**Important**: The default credentials in this guide are for development only!

For production:
1. Change the PostgreSQL password in `.env` and `docker-compose.yml`
2. Use strong, unique passwords
3. Consider using environment-specific configuration
4. Enable SSL/TLS for database connections
5. Restrict network access to PostgreSQL

## Next Steps

After successful migration:

1. Update your deployment scripts to use PostgreSQL
2. Configure automated backups for PostgreSQL
3. Monitor database performance
4. Consider setting up connection pooling for production
5. Update your CI/CD pipeline if applicable

## Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy PostgreSQL Dialect](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
