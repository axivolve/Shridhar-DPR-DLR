-- Add picture column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS picture TEXT;

-- Add picture column to simple_users table  
ALTER TABLE simple_users ADD COLUMN IF NOT EXISTS picture TEXT;

-- Update existing records to have empty picture field if null
UPDATE users SET picture = '' WHERE picture IS NULL;
UPDATE simple_users SET picture = '' WHERE picture IS NULL;
