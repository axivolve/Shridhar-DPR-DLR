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
from app.models import TokenResponse, WriteResponse, DocumentListResponse, SheetDataResponse
from app.mcp_client import mcp_client
from typing import Optional

app = FastAPI(title="Simple Google Sheets API with MCP", version="1.0.0")

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
        <title>Google Sheets API with MCP Test</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
            .button { 
                background-color: #4285f4; color: white; padding: 12px 24px; 
                border: none; border-radius: 4px; font-size: 16px; cursor: pointer; 
                text-decoration: none; display: inline-block; margin: 10px;
            }
            .button:hover { background-color: #357ae8; }
            .mcp-button { background-color: #34a853; }
            .mcp-button:hover { background-color: #2d8f46; }
        </style>
    </head>
    <body>
        <h1>Google Sheets API with MCP Integration</h1>
        <p>Click the button below to sign in with Google and test the API</p>
        <a href="/auth/login" class="button">🔐 Sign in with Google</a>
        
        <div style="margin-top: 50px; padding: 20px; border: 1px solid #ddd; max-width: 800px; margin-left: auto; margin-right: auto;">
            <h3>Available Features:</h3>
            <div style="text-align: left;">
                <h4>📊 Basic Features:</h4>
                <ul>
                    <li><strong>GET /documents</strong> - List all your Google Sheets</li>
                    <li><strong>POST /write-hello-world/{sheet_id}</strong> - Write "Hello World" to a sheet</li>
                    <li><strong>GET /user/me</strong> - Get your user information</li>
                </ul>
                
                <h4>🤖 MCP-Powered Features:</h4>
                <ul>
                    <li><strong>GET /mcp/sheet-data/{sheet_id}</strong> - Get sheet data using MCP</li>
                    <li><strong>POST /mcp/analyze-sheet/{sheet_id}</strong> - AI analysis of sheet data</li>
                </ul>
                
                <h4>How to test:</h4>
                <ol>
                    <li>Click "Sign in with Google" above</li>
                    <li>After login, copy your JWT token</li>
                    <li>Visit <a href="/docs">/docs</a> for interactive testing</li>
                    <li>Use Authorization header: <code>Bearer YOUR_TOKEN</code></li>
                </ol>
            </div>
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
            .feature-box {{
                background: #e8f5e8; padding: 15px; margin: 20px;
                border-radius: 5px; border-left: 4px solid #34a853;
            }}
        </style>
    </head>
    <body>
        <h1>✅ Authentication Successful!</h1>
        <p>Welcome, {result['user']['name']}!</p>
        
        <h3>Your JWT Token:</h3>
        <div class="token-box" id="token">{result['access_token']}</div>
        <button class="copy-btn" onclick="copyToken()">Copy Token</button>
        
        <div class="feature-box">
            <h3>🤖 MCP Features Now Available!</h3>
            <p>You can now use MCP-powered features to analyze and interact with your Google Sheets using AI.</p>
        </div>
        
        <div style="margin-top: 30px;">
            <h3>Next Steps:</h3>
            <p>1. Copy the token above</p>
            <p>2. Visit <a href="/docs">/docs</a> to test the API</p>
            <p>3. Use Authorization header: <code>Bearer YOUR_TOKEN</code></p>
            <p>4. Try the new MCP endpoints for advanced sheet analysis!</p>
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

# Original endpoints
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

# New MCP-powered endpoints
@app.get("/mcp/sheet-data/{sheet_id}", response_model=SheetDataResponse)
async def get_sheet_data_mcp(
    sheet_id: str,
    sheet: str = "Sheet1",
    range_name: str = "A1:Z1000",
    current_user: dict = Depends(get_current_user)
):
    """
    Get sheet data using MCP integration with user's OAuth credentials.
    This provides more structured data access compared to direct API calls.
    """
    try:
        result = await mcp_client.get_sheet_data_with_user_auth(
            google_id=current_user['google_id'],
            spreadsheet_id=sheet_id,
            sheet=sheet,
            range_name=range_name
        )
        
        if not result.get('success', False):
            raise HTTPException(status_code=500, detail=result.get('error', 'Unknown error'))
        
        return SheetDataResponse(**result)
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MCP error: {str(e)}")

@app.post("/mcp/analyze-sheet/{sheet_id}")
async def analyze_sheet_data(
    sheet_id: str,
    sheet: str = "Sheet1",
    range_name: str = "A1:Z1000",
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze sheet data and provide insights.
    This demonstrates how MCP can be used for AI-powered data analysis.
    """
    try:
        # First, get the sheet data
        sheet_data = await mcp_client.get_sheet_data_with_user_auth(
            google_id=current_user['google_id'],
            spreadsheet_id=sheet_id,
            sheet=sheet,
            range_name=range_name
        )
        
        if not sheet_data.get('success', False):
            raise HTTPException(status_code=500, detail=sheet_data.get('error', 'Failed to get sheet data'))
        
        data = sheet_data.get('data', [])
        
        if not data:
            return {
                "success": True,
                "analysis": "Sheet appears to be empty or no data in the specified range.",
                "sheet_info": sheet_data
            }
        
        # Basic analysis
        analysis = {
            "row_count": len(data),
            "column_count": len(data[0]) if data else 0,
            "has_headers": True if data and len(data) > 1 else False,
            "headers": data[0] if data else [],
            "sample_data": data[1:6] if len(data) > 1 else [],  # First 5 data rows
            "data_types": [],
            "summary": ""
        }
        
        # Analyze data types in each column
        if len(data) > 1:
            for col_idx in range(len(data[0])):
                col_values = [row[col_idx] if col_idx < len(row) else '' for row in data[1:]]
                col_values = [v for v in col_values if v.strip()]  # Remove empty values
                
                if col_values:
                    # Simple type detection
                    numeric_count = sum(1 for v in col_values if v.replace('.', '').replace('-', '').isdigit())
                    if numeric_count > len(col_values) * 0.8:
                        analysis["data_types"].append("numeric")
                    else:
                        analysis["data_types"].append("text")
                else:
                    analysis["data_types"].append("empty")
        
        # Generate summary
        analysis["summary"] = f"Found {analysis['row_count']} rows and {analysis['column_count']} columns. "
        if analysis["has_headers"]:
            analysis["summary"] += f"Headers detected: {', '.join(analysis['headers'][:5])}{'...' if len(analysis['headers']) > 5 else ''}."
        
        return {
            "success": True,
            "sheet_id": sheet_id,
            "sheet": sheet,
            "range": range_name,
            "analysis": analysis,
            "raw_data_preview": data[:3] if data else []  # First 3 rows for preview
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)