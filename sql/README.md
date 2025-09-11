# Database Setup for AI Works Tracker

This directory contains all the necessary SQL migrations and setup scripts for the AI Works Tracker authentication system.

## Quick Setup

### Option 1: Run the Complete Migration (Recommended)

1. **Copy the SQL**: Open `complete_auth_migration.sql`
2. **Go to Supabase Dashboard**: Navigate to your project's SQL Editor
3. **Paste and Run**: Copy the entire SQL content and execute it

### Option 2: Use the Python Setup Script

1. **Set Environment Variables**:
   ```bash
   export SUPABASE_URL="your_supabase_url"
   export SUPABASE_ANON_KEY="your_supabase_anon_key"
   ```

2. **Run the Setup Script**:
   ```bash
   python sql/setup_database.py
   ```

## What Gets Created

### Tables
- **`simple_users`**: Stores basic authentication data (mobile, password, name, etc.)
- **`users`**: Stores Google OAuth data

### Indexes
- Mobile number lookups
- Google ID lookups
- Email lookups

### Triggers
- Automatic `updated_at` timestamp updates

### Views
- **`user_auth_summary`**: Easy user management view

## Individual Migration Files

If you prefer to run migrations individually:

1. **`create_simple_users_table.sql`**: Basic user table
2. **`create_users_table.sql`**: Google OAuth table  
3. **`add_password_column.sql`**: Adds password field
4. **`add_picture_column.sql`**: Adds picture field

## Verification

After running the migration, you can verify it worked by checking:

```sql
-- Check if tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('simple_users', 'users');

-- Check if indexes exist
SELECT indexname FROM pg_indexes 
WHERE tablename IN ('simple_users', 'users');

-- Check if triggers exist
SELECT trigger_name FROM information_schema.triggers 
WHERE event_object_table IN ('simple_users', 'users');
```

## Troubleshooting

### Common Issues

1. **Permission Denied**: Make sure you're using the service role key, not the anon key
2. **Table Already Exists**: The migration uses `IF NOT EXISTS` so it's safe to run multiple times
3. **Constraint Conflicts**: The migration handles dropping old constraints before adding new ones

### Reset Database (Development Only)

If you need to start fresh:

```sql
-- WARNING: This will delete all data!
DROP TABLE IF EXISTS simple_users CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
```

Then run the complete migration again.

## Production Notes

- Remove the sample user insertion in production
- Consider adding additional indexes based on your query patterns
- Set up proper backup strategies
- Monitor database performance
