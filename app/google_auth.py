from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import json
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.config import *
from app.database import save_user, get_user_tokens
from typing import Optional
from fastapi import HTTPException

def create_google_auth_flow():
    """Create Google OAuth2 flow"""
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [GOOGLE_REDIRECT_URI]
            }
        },
        scopes=GOOGLE_SCOPES
    )
    flow.redirect_uri = GOOGLE_REDIRECT_URI
    return flow

def get_google_auth_url() -> str:
    """Get Google OAuth2 authorization URL"""
    flow = create_google_auth_flow()
    auth_url, _ = flow.authorization_url(prompt='consent')
    return auth_url

async def handle_google_callback(code: str) -> Optional[dict]:
    """Handle Google OAuth2 callback"""
    try:
        flow = create_google_auth_flow()
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        
        # Get user info from Google
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        
        # Prepare user data
        user_data = {
            'google_id': user_info['id'],
            'email': user_info['email'],
            'name': user_info['name'],
            'picture': user_info.get('picture', ''),
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token
        }
        
        # Save to database
        user = await save_user(user_data)
        
        if user:
            # Create JWT token
            jwt_token = create_jwt_token(user_data)
            return {
                'access_token': jwt_token,
                'user': user_data
            }
        
        return None
        
    except Exception as e:
        print(f"OAuth callback error: {e}")
        return None

def create_jwt_token(user_data: dict) -> str:
    """Create JWT token for user"""
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
    payload = {
        'google_id': user_data['google_id'],
        'email': user_data['email'],
        'exp': expire
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token: str) -> Optional[dict]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

async def write_hello_world_to_sheet(google_id: str, sheet_id: str) -> Optional[dict]:
    """Write 'Hello World' to Google Sheet"""
    try:
        # Get user tokens from database
        tokens = await get_user_tokens(google_id)
        if not tokens:
            return None
            
        # Create credentials
        credentials = Credentials(
            token=tokens['access_token'],
            refresh_token=tokens['refresh_token'],
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            token_uri="https://oauth2.googleapis.com/token"
        )
        
        # Refresh token if needed
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            # Update tokens in database
            await save_user({
                'google_id': google_id,
                'access_token': credentials.token,
                'refresh_token': credentials.refresh_token
            })
        
        # Build sheets service
        service = build('sheets', 'v4', credentials=credentials)
        
        # Write "Hello World" to cell A1
        range_name = 'Sheet1!A1'
        values = [['Hello World']]
        body = {'values': values}
        
        result = service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        return {
            'success': True,
            'message': 'Hello World written successfully!',
            'sheet_id': sheet_id,
            'range_written': range_name,
            'updated_cells': result.get('updatedCells', 0)
        }
        
    except Exception as e:
        print(f"Sheets API error: {e}")
        return {
            'success': False,
            'message': f'Error writing to sheet: {str(e)}',
            'sheet_id': sheet_id,
            'range_written': 'A1'
        }

async def list_google_sheets(google_id: str) -> list:
    """List all Google Sheets accessible by the user"""
    try:
        # Get user's tokens from database
        user_tokens = await get_user_tokens(google_id)
        if not user_tokens:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Create credentials from stored tokens
        creds = Credentials(
            token=user_tokens['access_token'],
            refresh_token=user_tokens.get('refresh_token'),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            scopes=GOOGLE_SCOPES
        )
        
        # Build the Drive API client
        service = build('drive', 'v3', credentials=creds)
        
        # List all Google Sheets files
        results = service.files().list(
            q="mimeType='application/vnd.google-apps.spreadsheet' and trashed=false",
            pageSize=100,
            fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime, webViewLink)"
        ).execute()
        
        return results.get('files', [])
        
    except Exception as e:
        print(f"Error listing Google Sheets: {str(e)}")
        if "invalid_grant" in str(e):
            raise HTTPException(status_code=401, detail="Session expired. Please sign in again.")
        raise HTTPException(status_code=500, detail=f"Error accessing Google Drive: {str(e)}")
