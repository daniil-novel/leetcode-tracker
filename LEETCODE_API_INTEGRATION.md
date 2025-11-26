# LeetCode API Integration Guide

## Overview

This project now includes direct integration with LeetCode's GraphQL API, allowing you to fetch user data, problem information, and statistics directly from LeetCode without manual data entry.

## Features Added

### 1. LeetCode API Client (`leetcode_tracker/leetcode_client.py`)

A comprehensive async client for interacting with LeetCode's GraphQL API:

- **User Profile**: Get complete user profile information
- **Solved Problems**: Fetch statistics on solved problems by difficulty
- **Submission Calendar**: Get user's submission calendar with activity data
- **Recent Submissions**: Retrieve recent submissions (all or accepted only)
- **Contest Information**: Get contest rankings and history
- **Badges**: Fetch user badges and upcoming badges
- **Daily Problem**: Get today's daily coding challenge
- **Problem Details**: Get detailed information about specific problems
- **Problems List**: Browse problems with filters (difficulty, tags, pagination)
- **Language Stats**: Get programming language usage statistics
- **Skill Stats**: Get skill-based problem-solving statistics

### 2. API Endpoints (`/api/leetcode/*`)

All endpoints require authentication (JWT token).

#### User Data Endpoints

- `GET /api/leetcode/{username}/profile` - Get user profile
- `GET /api/leetcode/{username}/solved` - Get solved problems count
- `GET /api/leetcode/{username}/calendar?year=2024` - Get submission calendar
- `GET /api/leetcode/{username}/submissions?limit=20` - Get recent submissions
- `GET /api/leetcode/{username}/ac-submissions?limit=20` - Get accepted submissions
- `GET /api/leetcode/{username}/contest` - Get contest info and history
- `GET /api/leetcode/{username}/badges` - Get user badges
- `GET /api/leetcode/{username}/language-stats` - Get language statistics
- `GET /api/leetcode/{username}/skill-stats` - Get skill statistics
- `GET /api/leetcode/{username}/sync` - Sync all user data in one call

#### Problem Endpoints

- `GET /api/leetcode/daily-problem` - Get today's daily challenge
- `GET /api/leetcode/problem/{title_slug}` - Get problem details
- `GET /api/leetcode/problems?limit=20&skip=0&difficulty=MEDIUM&tags=array,dp` - Browse problems

### 3. Database Changes

Added `leetcode_username` field to the User model to store LeetCode username for API synchronization.

**Migration**: `alembic/versions/ed721a9614c3_add_leetcode_username_to_users.py`

To apply the migration:
```bash
uv run alembic upgrade head
```

## Usage Examples

### 1. Get User Profile

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/leetcode/username123/profile
```

Response:
```json
{
  "username": "username123",
  "profile": {
    "realName": "John Doe",
    "userAvatar": "https://...",
    "ranking": 12345,
    "reputation": 100,
    "countryName": "United States"
  },
  "submitStats": {
    "acSubmissionNum": [
      {"difficulty": "All", "count": 500},
      {"difficulty": "Easy", "count": 200},
      {"difficulty": "Medium", "count": 250},
      {"difficulty": "Hard", "count": 50}
    ]
  }
}
```

### 2. Get Solved Problems Statistics

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/leetcode/username123/solved
```

Response:
```json
{
  "solvedProblem": 500,
  "easySolved": 200,
  "mediumSolved": 250,
  "hardSolved": 50
}
```

### 3. Get Submission Calendar

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/leetcode/username123/calendar?year=2024
```

Response:
```json
{
  "activeYears": [2023, 2024],
  "streak": 15,
  "totalActiveDays": 180,
  "submissionCalendar": "{\"1609459200\":3,\"1609545600\":5,...}"
}
```

### 4. Get Daily Problem

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/leetcode/daily-problem
```

Response:
```json
{
  "date": "2024-11-26",
  "link": "/problems/two-sum/",
  "question": {
    "questionId": "1",
    "questionFrontendId": "1",
    "title": "Two Sum",
    "titleSlug": "two-sum",
    "difficulty": "Easy",
    "topicTags": [
      {"name": "Array", "slug": "array"},
      {"name": "Hash Table", "slug": "hash-table"}
    ]
  }
}
```

### 5. Browse Problems with Filters

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "http://localhost:8000/api/leetcode/problems?limit=10&difficulty=MEDIUM&tags=array,dynamic-programming"
```

### 6. Sync All User Data

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/leetcode/username123/sync
```

This endpoint fetches profile, solved stats, calendar, and recent submissions in one call.

## Integration with Your Application

### Setting LeetCode Username

Users can set their LeetCode username in their profile settings. Add an endpoint to update the user's `leetcode_username` field:

```python
@router.put("/api/users/me/leetcode-username")
async def update_leetcode_username(
    leetcode_username: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.leetcode_username = leetcode_username
    db.commit()
    return {"message": "LeetCode username updated"}
```

### Auto-Sync Feature

You can create a background task to automatically sync LeetCode data:

```python
from fastapi import BackgroundTasks

async def sync_user_leetcode_data(username: str, user_id: int, db: Session):
    """Background task to sync LeetCode data"""
    client = get_leetcode_client()
    
    # Fetch recent accepted submissions
    submissions = await client.get_recent_ac_submissions(username, limit=50)
    
    # Process and save to database
    for submission in submissions:
        # Convert timestamp to date
        date = datetime.fromtimestamp(int(submission['timestamp'])).date()
        
        # Check if already exists
        existing = db.query(SolvedTask).filter(
            SolvedTask.user_id == user_id,
            SolvedTask.title == submission['title'],
            SolvedTask.date == date
        ).first()
        
        if not existing:
            # Create new task
            task = SolvedTask(
                user_id=user_id,
                date=date,
                title=submission['title'],
                difficulty=get_difficulty_from_slug(submission['titleSlug']),
                points=calculate_xp(difficulty),
                platform="leetcode"
            )
            db.add(task)
    
    db.commit()

@router.post("/api/sync-leetcode")
async def trigger_sync(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.leetcode_username:
        raise HTTPException(400, "LeetCode username not set")
    
    background_tasks.add_task(
        sync_user_leetcode_data,
        current_user.leetcode_username,
        current_user.id,
        db
    )
    
    return {"message": "Sync started in background"}
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

All LeetCode endpoints will be documented under the "leetcode" tag.

## Rate Limiting Considerations

LeetCode's API doesn't have official rate limits documented, but it's good practice to:

1. Cache responses when possible
2. Implement exponential backoff on errors
3. Limit concurrent requests
4. Add delays between bulk operations

## Error Handling

The client includes comprehensive error handling:

- **404**: User or problem not found
- **500**: LeetCode API errors or network issues
- **GraphQL Errors**: Logged and re-raised with details

## Technical Details

### GraphQL Queries

All queries are optimized to fetch only necessary data. The client uses LeetCode's official GraphQL endpoint:
- **URL**: `https://leetcode.com/graphql`
- **Method**: POST
- **Content-Type**: application/json

### Async Implementation

The client uses `httpx.AsyncClient` for non-blocking I/O, making it suitable for high-concurrency scenarios.

### Singleton Pattern

The client uses a singleton pattern to reuse HTTP connections:
```python
client = get_leetcode_client()  # Returns the same instance
```

### Cleanup

The client is properly closed on application shutdown via the lifecycle event handler in `main.py`.

## Future Enhancements

Potential improvements:

1. **Caching Layer**: Add Redis caching for frequently accessed data
2. **Webhooks**: Notify users when new submissions are detected
3. **Batch Operations**: Sync multiple users concurrently
4. **Analytics**: Track problem-solving patterns and trends
5. **Recommendations**: Suggest problems based on user's skill level
6. **Contest Reminders**: Notify users about upcoming contests

## Troubleshooting

### "User not found" Error

- Verify the LeetCode username is correct (case-sensitive)
- Check if the user's profile is public on LeetCode

### Timeout Errors

- LeetCode's API might be slow or down
- Increase timeout in `leetcode_client.py` if needed

### GraphQL Errors

- Check the error message in logs
- LeetCode might have changed their API schema
- Update queries in `leetcode_client.py` accordingly

## References

- [LeetCode GraphQL API](https://leetcode.com/graphql)
- [alfa-leetcode-api](https://github.com/alfaarghya/alfa-leetcode-api) - Reference implementation
- [LeetCode API Documentation](https://alfaarghya.github.io/alfa-leetcode-api/)

## Support

For issues or questions:
1. Check the application logs
2. Review the API documentation at `/docs`
3. Open an issue on GitHub
