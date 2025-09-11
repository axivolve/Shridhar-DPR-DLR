-- Complete Authentication Migration
-- This migration sets up the entire authentication system for AI Works Tracker

-- 1. Create simple_users table for basic authentication
CREATE TABLE IF NOT EXISTS simple_users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    mobile_number VARCHAR(10) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    username VARCHAR(100),
    picture VARCHAR(500),
    google_id VARCHAR(255),
    access_token TEXT,
    refresh_token TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure unique mobile number
    UNIQUE(mobile_number),
    
    -- Ensure unique username if provided
    UNIQUE(username)
);

-- 2. Create users table for Google OAuth (if not exists)
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    google_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    picture VARCHAR(500),
    access_token TEXT,
    refresh_token TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_simple_users_mobile ON simple_users(mobile_number);
CREATE INDEX IF NOT EXISTS idx_simple_users_google_id ON simple_users(google_id);
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- 4. Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 5. Create triggers to automatically update updated_at
CREATE TRIGGER update_simple_users_updated_at 
    BEFORE UPDATE ON simple_users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 6. Add any missing columns to existing tables (if they exist)
-- This handles cases where tables might already exist but are missing columns

-- Add password column to simple_users if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'simple_users' AND column_name = 'password'
    ) THEN
        ALTER TABLE simple_users ADD COLUMN password VARCHAR(255);
    END IF;
END $$;

-- Add picture column to simple_users if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'simple_users' AND column_name = 'picture'
    ) THEN
        ALTER TABLE simple_users ADD COLUMN picture VARCHAR(500);
    END IF;
END $$;

-- 7. Update constraints to ensure proper uniqueness
-- Drop old constraints if they exist
ALTER TABLE simple_users DROP CONSTRAINT IF EXISTS simple_users_mobile_number_email_key;
ALTER TABLE simple_users DROP CONSTRAINT IF EXISTS simple_users_mobile_number_unique;

-- Add new constraints
ALTER TABLE simple_users ADD CONSTRAINT simple_users_mobile_number_unique UNIQUE(mobile_number);

-- 8. Create a view for easy user management (optional)
CREATE OR REPLACE VIEW user_auth_summary AS
SELECT 
    id,
    mobile_number,
    email,
    name,
    username,
    CASE 
        WHEN google_id IS NOT NULL THEN 'Google Linked'
        ELSE 'Basic Auth Only'
    END as auth_status,
    created_at,
    updated_at
FROM simple_users
ORDER BY created_at DESC;

-- 9. Insert a sample user for testing (optional - remove in production)
-- INSERT INTO simple_users (mobile_number, password, email, name, username) 
-- VALUES ('1234567890', 'password123', 'test@example.com', 'Test User', 'testuser')
-- ON CONFLICT (mobile_number) DO NOTHING;

-- Migration completed successfully
SELECT 'Authentication migration completed successfully!' as status;
