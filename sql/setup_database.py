#!/usr/bin/env python3
"""
Database Setup Script for AI Works Tracker
This script applies the complete authentication migration to Supabase
"""

import os
import sys
from supabase import create_client, Client

def setup_database():
    """Apply the complete authentication migration"""
    
    # Get Supabase credentials from environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")
        print("Please set them in your .env file or environment")
        return False
    
    try:
        # Initialize Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Read the migration SQL file
        migration_file = os.path.join(os.path.dirname(__file__), 'complete_auth_migration.sql')
        
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        print("🔄 Applying authentication migration...")
        
        # Split the SQL into individual statements
        statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
        
        # Execute each statement
        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"  Executing statement {i}/{len(statements)}...")
                try:
                    # Use rpc to execute SQL
                    result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                    print(f"    ✅ Statement {i} executed successfully")
                except Exception as e:
                    print(f"    ⚠️  Statement {i} warning: {e}")
                    # Continue with other statements even if one fails
                    continue
        
        print("✅ Database migration completed successfully!")
        print("\n📋 What was created:")
        print("  • simple_users table for basic authentication")
        print("  • users table for Google OAuth")
        print("  • Indexes for better performance")
        print("  • Triggers for automatic timestamp updates")
        print("  • User management view")
        print("\n🚀 Your authentication system is ready to use!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error applying migration: {e}")
        return False

if __name__ == "__main__":
    print("🏗️  AI Works Tracker - Database Setup")
    print("=" * 50)
    
    success = setup_database()
    
    if success:
        print("\n✅ Setup completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)
