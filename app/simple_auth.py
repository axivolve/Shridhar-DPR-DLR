from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_HOURS
from app.database import (
    create_simple_user, 
    get_simple_user_by_mobile_email,
    get_simple_user_by_mobile,
    update_simple_user_profile,
    update_simple_user_google_data,
    get_simple_user_by_id
)
from app.models import SimpleUser, AuthResponse
from typing import Optional
import re

def validate_mobile_number(mobile_number: str) -> bool:
    """Validate mobile number format"""
    # Basic validation for mobile number (10 digits)
    pattern = r'^[0-9]{10}$'
    return bool(re.match(pattern, mobile_number))

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def create_simple_jwt_token(user_data: dict) -> str:
    """Create JWT token for simple user"""
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
    payload = {
        'user_id': user_data['id'],
        'mobile_number': user_data['mobile_number'],
        'email': user_data['email'],
        'exp': expire
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_simple_jwt_token(token: str) -> Optional[dict]:
    """Verify JWT token for simple user"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

async def handle_signup(mobile_number: str, password: str, email: str, name: str) -> AuthResponse:
    """Handle user signup"""
    try:
        # Validate inputs
        if not validate_mobile_number(mobile_number):
            return AuthResponse(
                success=False,
                message="Invalid mobile number format",
                error="Mobile number must be 10 digits"
            )
        
        if not validate_email(email):
            return AuthResponse(
                success=False,
                message="Invalid email format",
                error="Please provide a valid email address"
            )
        
        if not password or len(password) < 6:
            return AuthResponse(
                success=False,
                message="Invalid password",
                error="Password must be at least 6 characters"
            )
        
        if not name or not name.strip():
            return AuthResponse(
                success=False,
                message="Invalid name",
                error="Name is required"
            )
        
        # Check if user already exists
        existing_user = await get_simple_user_by_mobile_email(mobile_number, email)
        if existing_user:
            return AuthResponse(
                success=False,
                message="User already exists",
                error="A user with this mobile number and email already exists"
            )
        
        # Create new user
        user_data = {
            'mobile_number': mobile_number,
            'password': password,  # In production, hash this password
            'email': email,
            'name': name.strip()
        }
        
        user = await create_simple_user(user_data)
        if not user:
            return AuthResponse(
                success=False,
                message="Failed to create user",
                error="Database error occurred"
            )
        
        # Create JWT token
        token = create_simple_jwt_token(user.dict())
        
        return AuthResponse(
            success=True,
            message="User created successfully. Please complete your profile.",
            user_id=str(user.id),
            token=token,
            user=user.dict(),
            requires_profile_completion=True
        )
        
    except Exception as e:
        return AuthResponse(
            success=False,
            message="Signup failed",
            error=str(e)
        )

async def handle_login(mobile_number: str, password: str) -> AuthResponse:
    """Handle user login"""
    try:
        # Validate inputs
        if not validate_mobile_number(mobile_number):
            return AuthResponse(
                success=False,
                message="Invalid mobile number format",
                error="Mobile number must be 10 digits"
            )
        
        if not password or len(password) < 6:
            return AuthResponse(
                success=False,
                message="Invalid password",
                error="Password must be at least 6 characters"
            )
        
        # Check if user exists by mobile number
        user = await get_simple_user_by_mobile(mobile_number)
        if not user:
            return AuthResponse(
                success=False,
                message="User not found",
                error="No user found with this mobile number"
            )
        
        # Validate password
        if user.password != password:  # In production, use proper password hashing
            return AuthResponse(
                success=False,
                message="Invalid password",
                error="Incorrect password"
            )
        
        # Create JWT token
        token = create_simple_jwt_token(user.dict())
        
        # Check if profile is complete
        requires_profile_completion = not (user.name and user.username)
        
        return AuthResponse(
            success=True,
            message="Login successful",
            user_id=str(user.id),
            token=token,
            user=user.dict(),
            requires_profile_completion=requires_profile_completion
        )
        
    except Exception as e:
        return AuthResponse(
            success=False,
            message="Login failed",
            error=str(e)
        )

async def handle_profile_completion(user_id: str, name: str, username: str) -> AuthResponse:
    """Handle profile completion"""
    try:
        # Validate inputs
        if not name or not name.strip():
            return AuthResponse(
                success=False,
                message="Name is required",
                error="Please provide a valid name"
            )
        
        if not username or not username.strip():
            return AuthResponse(
                success=False,
                message="Username is required",
                error="Please provide a valid username"
            )
        
        # Update user profile
        user = await update_simple_user_profile(user_id, name.strip(), username.strip())
        if not user:
            return AuthResponse(
                success=False,
                message="Failed to update profile",
                error="Database error occurred"
            )
        
        # Create new JWT token with updated data
        token = create_simple_jwt_token(user.dict())
        
        return AuthResponse(
            success=True,
            message="Profile completed successfully",
            user_id=str(user.id),
            token=token,
            requires_profile_completion=False
        )
        
    except Exception as e:
        return AuthResponse(
            success=False,
            message="Profile completion failed",
            error=str(e)
        )

async def handle_google_oauth_callback(user_id: str, google_data: dict) -> AuthResponse:
    """Handle Google OAuth callback for simple user"""
    try:
        # Update user with Google data
        user = await update_simple_user_google_data(
            user_id=user_id,
            google_id=google_data['google_id'],
            access_token=google_data['access_token'],
            refresh_token=google_data.get('refresh_token'),
            name=google_data.get('name'),
            picture=google_data.get('picture')
        )
        
        if not user:
            return AuthResponse(
                success=False,
                message="Failed to link Google account",
                error="Database error occurred"
            )
        
        # Create new JWT token with Google data
        token = create_simple_jwt_token(user.dict())
        
        return AuthResponse(
            success=True,
            message="Google account linked successfully",
            user_id=str(user.id),
            token=token,
            requires_profile_completion=False
        )
        
    except Exception as e:
        return AuthResponse(
            success=False,
            message="Google account linking failed",
            error=str(e)
        )
