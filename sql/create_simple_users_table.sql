-- Create simple_users table for basic authentication
CREATE TABLE IF NOT EXISTS simple_users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    mobile_number VARCHAR(10) NOT NULL,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    username VARCHAR(100),
    google_id VARCHAR(255),
    access_token TEXT,
    refresh_token TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure unique combination of mobile and email
    UNIQUE(mobile_number, email),
    
    -- Ensure unique username if provided
    UNIQUE(username)
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_simple_users_mobile_email ON simple_users(mobile_number, email);
CREATE INDEX IF NOT EXISTS idx_simple_users_google_id ON simple_users(google_id);

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_simple_users_updated_at 
    BEFORE UPDATE ON simple_users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
