from supabase import create_client, Client
from app.config import SUPABASE_URL, SUPABASE_KEY
from app.models import User
from typing import Optional
import json

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def create_user_table():
    """Create users table if it doesn't exist"""
    # This will be created manually in Supabase dashboard or via SQL
    pass

async def save_user(user_data: dict) -> Optional[User]:
    """Save or update user in database"""
    try:
        # Check if user exists
        existing = supabase.table('users').select('*').eq('google_id', user_data['google_id']).execute()
        
        if existing.data:
            # Update existing user
            result = supabase.table('users').update({
                'email': user_data['email'],
                'name': user_data['name'],
                'access_token': user_data['access_token'],
                'refresh_token': user_data.get('refresh_token'),
                'updated_at': 'now()'
            }).eq('google_id', user_data['google_id']).execute()
        else:
            # Create new user
            result = supabase.table('users').insert({
                'google_id': user_data['google_id'],
                'email': user_data['email'],
                'name': user_data['name'],
                'access_token': user_data['access_token'],
                'refresh_token': user_data.get('refresh_token'),
                'created_at': 'now()',
                'updated_at': 'now()'
            }).execute()
        
        if result.data:
            return User(**result.data[0])
        return None
        
    except Exception as e:
        print(f"Database error: {e}")
        return None

async def get_user_by_google_id(google_id: str) -> Optional[User]:
    """Get user by Google ID"""
    try:
        result = supabase.table('users').select('*').eq('google_id', google_id).execute()
        if result.data:
            return User(**result.data[0])
        return None
    except Exception as e:
        print(f"Database error: {e}")
        return None

async def get_user_tokens(google_id: str) -> Optional[dict]:
    """Get user's tokens"""
    try:
        result = supabase.table('users').select('access_token, refresh_token').eq('google_id', google_id).execute()
        if result.data:
            return {
                'access_token': result.data[0]['access_token'],
                'refresh_token': result.data[0]['refresh_token']
            }
        return None
    except Exception as e:
        print(f"Database error: {e}")
        return None
