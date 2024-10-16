# Database Setup - Conversation Memory

This directory contains the database schema for the conversation memory feature (Day 6).

## 📋 Requirements

- PostgreSQL 12+ (with UUID support)
- Database user with CREATE TABLE permissions

## 🚀 Quick Setup

### 1. Install PostgreSQL

**macOS (Homebrew)**:
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows**:
Download installer from https://www.postgresql.org/download/windows/

### 2. Create Database

```bash
# Connect to PostgreSQL
psql postgres

# Create database
CREATE DATABASE eligibility_agent;

# Create user (optional, use 'postgres' for local dev)
CREATE USER eligibility_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE eligibility_agent TO eligibility_user;

# Exit
\q
```

### 3. Apply Schema

```bash
# From project root
psql eligibility_agent < database/schema.sql

# Or connect and run manually
psql eligibility_agent
\i database/schema.sql
```

### 4. Configure Environment

Add to `.env`:
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/eligibility_agent
```

Replace `postgres:postgres` with your username:password if different.

## 📊 Database Schema

### Tables

1. **sessions** - Conversation sessions
   - `id`: UUID primary key
   - `session_key`: Client-facing identifier
   - `user_identifier`: Optional user info
   - `customer_profile`: JSONB customer data
   - `status`: active, completed, abandoned
   - `expires_at`: Auto-expiration (24h default)

2. **messages** - Conversation messages
   - `id`: Auto-increment primary key
   - `session_id`: Foreign key to sessions
   - `role`: user, assistant, tool, system
   - `content`: Message text
   - `tool_name`, `tool_input`, `tool_output`: Tool tracking

### Views

- **conversation_analytics** - Aggregated conversation stats

### Functions

- `cleanup_expired_sessions()` - Remove old sessions (call from cron)

## 🔍 Verify Setup

```bash
# Connect to database
psql eligibility_agent

# List tables
\dt

# Should show:
# sessions
# messages

# List views
\dv

# Should show:
# conversation_analytics

# Test query
SELECT COUNT(*) FROM sessions;

# Exit
\q
```

## 🧪 Test with API

Once database is set up, test the conversation memory:

```bash
# Start API
uvicorn app.main:app --reload

# Test query endpoint (creates session)
curl -X POST http://localhost:8000/api/v2/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "I am 35 years old, can I get life insurance?"
  }'

# Response will include session_key - save it!
# {
#   "answer": "...",
#   "session_key": "abc-123-def-456",
#   ...
# }

# Continue conversation (agent remembers context!)
curl -X POST http://localhost:8000/api/v2/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What about health insurance?",
    "session_key": "abc-123-def-456"
  }'
```

## 🛠️ Maintenance

### View Active Sessions

```sql
SELECT
    session_key,
    created_at,
    status,
    expires_at
FROM sessions
WHERE status = 'active'
  AND expires_at > NOW()
ORDER BY created_at DESC;
```

### View Conversation

```sql
SELECT
    role,
    content,
    created_at
FROM messages
WHERE session_id = 'YOUR_SESSION_UUID'
ORDER BY created_at ASC;
```

### Cleanup Expired Sessions

```sql
-- Manual cleanup
SELECT cleanup_expired_sessions();

-- Shows number of deleted sessions
```

### Setup Automatic Cleanup (Optional)

Add to crontab to run daily at 2 AM:

```bash
crontab -e

# Add this line:
0 2 * * * psql eligibility_agent -c "SELECT cleanup_expired_sessions();"
```

## 🐛 Troubleshooting

### Connection Refused

```bash
# Check PostgreSQL is running
brew services list  # macOS
sudo systemctl status postgresql  # Linux

# Start if needed
brew services start postgresql@15  # macOS
sudo systemctl start postgresql  # Linux
```

### Authentication Failed

1. Check `DATABASE_URL` in `.env`
2. Verify user/password with:
```bash
psql -U postgres -d eligibility_agent
```

### Permission Denied

```bash
# Grant permissions
psql postgres
GRANT ALL PRIVILEGES ON DATABASE eligibility_agent TO your_user;
\q
```

### UUID Extension Not Found

```bash
# Install UUID extension
psql eligibility_agent
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
\q
```

Modern PostgreSQL (12+) has `gen_random_uuid()` built-in, so this shouldn't be needed.

## 📈 Production Considerations

For production deployment:

1. **Connection Pooling**: Use pgBouncer or similar
2. **Backups**: Setup automated backups
3. **Monitoring**: Track session creation rate, message volume
4. **Indexes**: Already included in schema for common queries
5. **Partitioning**: Consider partitioning `messages` table by date if volume is high
6. **Cleanup Job**: Schedule automatic cleanup (cron or similar)

## 🔗 Related Files

- `schema.sql` - Database schema definition
- `app/session_manager.py` - Python interface to database
- `app/agent.py` - Agent with session integration
- `app/main.py` - API endpoints using sessions
