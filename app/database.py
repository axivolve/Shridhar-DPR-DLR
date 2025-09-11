from supabase import create_client, Client
from app.config import SUPABASE_URL, SUPABASE_KEY
from app.models import User, SimpleUser
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
                'picture': user_data.get('picture', ''),
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
                'picture': user_data.get('picture', ''),
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

# Simple Authentication Functions
async def create_simple_user(user_data: dict) -> Optional[SimpleUser]:
    """Create a new simple user"""
    try:
        result = supabase.table('simple_users').insert({
            'mobile_number': user_data['mobile_number'],
            'password': user_data['password'],
            'email': user_data['email'],
            'name': user_data.get('name'),
            'created_at': 'now()',
            'updated_at': 'now()'
        }).execute()
        
        if result.data:
            return SimpleUser(**result.data[0])
        return None
    except Exception as e:
        print(f"Database error creating simple user: {e}")
        return None

async def get_simple_user_by_mobile_email(mobile_number: str, email: str) -> Optional[SimpleUser]:
    """Get simple user by mobile number and email"""
    try:
        result = supabase.table('simple_users').select('*').eq('mobile_number', mobile_number).eq('email', email).execute()
        if result.data:
            return SimpleUser(**result.data[0])
        return None
    except Exception as e:
        print(f"Database error getting simple user: {e}")
        return None

async def get_simple_user_by_mobile(mobile_number: str) -> Optional[SimpleUser]:
    """Get simple user by mobile number only"""
    try:
        result = supabase.table('simple_users').select('*').eq('mobile_number', mobile_number).execute()
        if result.data:
            return SimpleUser(**result.data[0])
        return None
    except Exception as e:
        print(f"Database error getting simple user by mobile: {e}")
        return None

async def update_simple_user_profile(user_id: str, name: str, username: str) -> Optional[SimpleUser]:
    """Update simple user profile with name and username"""
    try:
        result = supabase.table('simple_users').update({
            'name': name,
            'username': username,
            'updated_at': 'now()'
        }).eq('id', user_id).execute()
        
        if result.data:
            return SimpleUser(**result.data[0])
        return None
    except Exception as e:
        print(f"Database error updating simple user profile: {e}")
        return None

async def update_simple_user_google_data(user_id: str, google_id: str, access_token: str, refresh_token: str = None, name: str = None, picture: str = None) -> Optional[SimpleUser]:
    """Update simple user with Google OAuth data"""
    try:
        update_data = {
            'google_id': google_id,
            'access_token': access_token,
            'updated_at': 'now()'
        }
        if refresh_token:
            update_data['refresh_token'] = refresh_token
        if name:
            update_data['name'] = name
        if picture:
            update_data['picture'] = picture
            
        result = supabase.table('simple_users').update(update_data).eq('id', user_id).execute()
        
        if result.data:
            return SimpleUser(**result.data[0])
        return None
    except Exception as e:
        print(f"Database error updating simple user Google data: {e}")
        return None

async def get_simple_user_by_id(user_id: str) -> Optional[SimpleUser]:
    """Get simple user by ID"""
    try:
        result = supabase.table('simple_users').select('*').eq('id', user_id).execute()
        if result.data:
            return SimpleUser(**result.data[0])
        return None
    except Exception as e:
        print(f"Database error getting simple user by ID: {e}")
        return None
