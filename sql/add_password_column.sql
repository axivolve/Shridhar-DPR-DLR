-- Add password column to simple_users table
ALTER TABLE simple_users ADD COLUMN IF NOT EXISTS password VARCHAR(255);

-- Update the unique constraint to only be on mobile_number since we're now using password-based auth
-- First drop the existing constraint
ALTER TABLE simple_users DROP CONSTRAINT IF EXISTS simple_users_mobile_number_email_key;

-- Add new unique constraint on mobile_number only
ALTER TABLE simple_users ADD CONSTRAINT simple_users_mobile_number_unique UNIQUE(mobile_number);

-- Update the index
DROP INDEX IF EXISTS idx_simple_users_mobile_email;
CREATE INDEX IF NOT EXISTS idx_simple_users_mobile ON simple_users(mobile_number);
