#!/bin/bash

# Chat History Implementation Test
echo "🚀 Starting Chat History Test Environment"
echo "========================================="

# Function to run backend
start_backend() {
    echo "📡 Starting Backend Server..."
    cd /Users/apple/Shridhar_DPR
    python run.py &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
}

# Function to run frontend  
start_frontend() {
    echo "🎨 Starting Frontend Server..."
    cd /Users/apple/Shridhar_DPR/frontend
    npm run dev &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
}

# Function to cleanup
cleanup() {
    echo "🧹 Cleaning up..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit 0
}

# Trap cleanup on script exit
trap cleanup EXIT INT TERM

# Check if database table exists
echo "📋 Please run this SQL in your Supabase SQL Editor first:"
echo "------------------------------------------------------"
cat /Users/apple/Shridhar_DPR/sql/create_chat_history_table.sql
echo "------------------------------------------------------"
echo ""

read -p "Have you run the SQL in Supabase? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "❌ Please run the SQL first, then restart this script"
    exit 1
fi

# Start services
start_backend
sleep 3
start_frontend

echo ""
echo "✅ Test Environment Ready!"
echo "📍 Backend: http://localhost:8000"
echo "📍 Frontend: http://localhost:3000 (or 3001)"
echo ""
echo "🧪 Test Cases:"
echo "1. Login with User 1 (mobile: 9510595426, name: Ashish)"
echo "2. Select a spreadsheet and have some conversations"
echo "3. Use date dropdown to view history"
echo "4. Login with User 2 (mobile: 7096395426, name: Mohit)"
echo "5. Verify User 2 only sees their own history"
echo "6. Test same Google account with different mobile numbers"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user input to keep script running
wait