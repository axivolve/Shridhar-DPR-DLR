-- Chat History Table for User-Specific Conversations
-- Run this SQL in your Supabase SQL Editor

CREATE TABLE chat_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    mobile_number VARCHAR(15) NOT NULL,
    user_name VARCHAR(100),
    sheet_id VARCHAR(100) NOT NULL,
    sheet_name VARCHAR(200),
    message_type VARCHAR(20) NOT NULL CHECK (message_type IN ('user', 'assistant')),
    content TEXT NOT NULL,
    mode VARCHAR(20) DEFAULT 'dpr' CHECK (mode IN ('dpr', 'dlr', 'logs', 'planned')),
    conversation_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX idx_chat_history_mobile_sheet ON chat_history(mobile_number, sheet_id);
CREATE INDEX idx_chat_history_date ON chat_history(conversation_date);
CREATE INDEX idx_chat_history_mobile_date ON chat_history(mobile_number, conversation_date);
CREATE INDEX idx_chat_history_created_at ON chat_history(created_at);

-- Enable Row Level Security (RLS) for data protection
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (optional - for additional security)
-- Policy to allow users to see only their own chat history
CREATE POLICY "Users can view their own chat history" ON chat_history
    FOR SELECT USING (true); -- We'll handle access control in the application layer

CREATE POLICY "Users can insert their own chat history" ON chat_history
    FOR INSERT WITH CHECK (true); -- We'll handle access control in the application layer

-- Add comments for documentation
COMMENT ON TABLE chat_history IS 'Stores chat conversation history per user (mobile_number) and per spreadsheet';
COMMENT ON COLUMN chat_history.mobile_number IS 'User mobile number - unique identifier for chat segregation';
COMMENT ON COLUMN chat_history.sheet_id IS 'Google Sheets ID to separate conversations per spreadsheet';
COMMENT ON COLUMN chat_history.message_type IS 'Either user message or assistant response';
COMMENT ON COLUMN chat_history.conversation_date IS 'Date of conversation for date-wise filtering';
COMMENT ON COLUMN chat_history.mode IS 'Chat mode: dpr, dlr, logs, or planned';