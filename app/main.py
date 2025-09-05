from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse
from app.google_auth import (
    get_google_auth_url, 
    handle_google_callback, 
    verify_jwt_token,
    write_hello_world_to_sheet,
    list_google_sheets
)
from app.models import TokenResponse, WriteResponse, DocumentListResponse
from typing import Optional

app = FastAPI(title="Simple Google Sheets API", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Security
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    token = credentials.credentials
    user_data = verify_jwt_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_data

@app.get("/", response_class=HTMLResponse)
async def home():
    """Home page with login button"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Google Sheets API Test</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; margin-top: 100px; }
            .button { 
                background-color: #4285f4; color: white; padding: 12px 24px; 
                border: none; border-radius: 4px; font-size: 16px; cursor: pointer; 
                text-decoration: none; display: inline-block;
            }
            .button:hover { background-color: #357ae8; }
        </style>
    </head>
    <body>
        <h1>Google Sheets API Test</h1>
        <p>Click the button below to sign in with Google and test the API</p>
        <a href="/auth/login" class="button">🔐 Sign in with Google</a>
        
        <div style="margin-top: 50px; padding: 20px; border: 1px solid #ddd; max-width: 600px; margin-left: auto; margin-right: auto;">
            <h3>How to test:</h3>
            <ol style="text-align: left;">
                <li>Click "Sign in with Google" above</li>
                <li>After login, copy your JWT token</li>
                <li>Use the token to call: <code>POST /write-hello-world/{your_sheet_id}</code></li>
                <li>Or visit <a href="/docs">/docs</a> for interactive testing</li>
            </ol>
        </div>
    </body>
    </html>
    """

@app.get("/auth/login")
async def login():
    """Redirect to Google OAuth2"""
    auth_url = get_google_auth_url()
    return RedirectResponse(url=auth_url)

@app.get("/auth/callback")
async def callback(code: str):
    """Handle Google OAuth2 callback"""
    result = await handle_google_callback(code)
    
    if not result:
        raise HTTPException(status_code=400, detail="Authentication failed")
    
    # Return success page with token
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Authentication Success</title>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }}
            .token-box {{ 
                background: #f5f5f5; padding: 15px; margin: 20px; 
                border-radius: 5px; word-break: break-all; font-family: monospace;
            }}
            .copy-btn {{ 
                background: #4285f4; color: white; padding: 8px 16px; 
                border: none; border-radius: 4px; cursor: pointer; margin-left: 10px;
            }}
        </style>
    </head>
    <body>
        <h1>✅ Authentication Successful!</h1>
        <p>Welcome, {result['user']['name']}!</p>
        
        <h3>Your JWT Token:</h3>
        <div class="token-box" id="token">{result['access_token']}</div>
        <button class="copy-btn" onclick="copyToken()">Copy Token</button>
        
        <div style="margin-top: 30px;">
            <h3>Next Steps:</h3>
            <p>1. Copy the token above</p>
            <p>2. Visit <a href="/docs">/docs</a> to test the API</p>
            <p>3. Use Authorization header: <code>Bearer YOUR_TOKEN</code></p>
            <p>4. Call <code>POST /write-hello-world/YOUR_SHEET_ID</code></p>
        </div>
        
        <script>
            function copyToken() {{
                const token = document.getElementById('token').textContent;
                navigator.clipboard.writeText(token).then(() => {{
                    alert('Token copied to clipboard!');
                }});
            }}
        </script>
    </body>
    </html>
    """)

@app.post("/write-hello-world/{sheet_id}", response_model=WriteResponse)
async def write_hello_world(
    sheet_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Write 'Hello World' to Google Sheet at A1"""
    
    result = await write_hello_world_to_sheet(current_user['google_id'], sheet_id)
    
    if not result:
        raise HTTPException(status_code=500, detail="Failed to write to sheet")
    
    return WriteResponse(**result)

@app.get("/user/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "google_id": current_user['google_id'],
        "email": current_user['email'],
        "message": "Token is valid!"
    }

@app.get("/documents", response_model=DocumentListResponse)
async def show_document_list(current_user: dict = Depends(get_current_user)):
    """
    List all Google Sheets documents accessible by the user.
    Returns a list of documents with their metadata.
    """
    try:
        documents = await list_google_sheets(current_user['google_id'])
        return {"documents": documents}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
