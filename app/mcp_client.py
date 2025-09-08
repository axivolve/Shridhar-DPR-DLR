# app/mcp_client.py
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from urllib.parse import urlencode
import json
from typing import Optional, Dict, Any
from app.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_SCOPES
from app.database import get_user_tokens
from google.oauth2.credentials import Credentials

# MCP Configuration
MCP_SERVER_URL = "https://server.smithery.ai/@SmartManoj/google-sheets-mcp/mcp"
MCP_API_KEY = "fe120802-bad4-4434-bec8-11c2af683af4" 
MCP_PROFILE = "incredible-firefly-hQK5C9"

class MCPGoogleSheetsClient:
    def __init__(self):
        self.base_url = MCP_SERVER_URL
        self.api_key = MCP_API_KEY
        self.profile = MCP_PROFILE
    
    def _get_server_url(self) -> str:
        """Construct server URL with authentication"""
        params = {"api_key": self.api_key, "profile": self.profile}
        return f"{self.base_url}?{urlencode(params)}"
    
    async def get_sheet_data_with_user_auth(self, google_id: str, spreadsheet_id: str, sheet: str, range_name: str) -> Dict[str, Any]:
        """
        Get sheet data using user's OAuth credentials instead of service account
        """
        try:
            # Get user tokens from database
            tokens = await get_user_tokens(google_id)
            if not tokens:
                return {"error": "User not authenticated"}
            
            # Create credentials
            credentials = Credentials(
                token=tokens['access_token'],
                refresh_token=tokens['refresh_token'],
                client_id=GOOGLE_CLIENT_ID,
                client_secret=GOOGLE_CLIENT_SECRET,
                token_uri="https://oauth2.googleapis.com/token",
                scopes=GOOGLE_SCOPES
            )
            
            # For now, we'll use direct Google Sheets API instead of MCP
            # because MCP server expects service account credentials
            from googleapiclient.discovery import build
            from google.auth.transport.requests import Request
            
            # Refresh token if needed
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                # Update tokens in database
                from app.database import save_user
                await save_user({
                    'google_id': google_id,
                    'access_token': credentials.token,
                    'refresh_token': credentials.refresh_token
                })
            
            # Build sheets service
            service = build('sheets', 'v4', credentials=credentials)
            
            # Get sheet data
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet}!{range_name}"
            ).execute()
            
            values = result.get('values', [])
            
            return {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "sheet": sheet,
                "range": range_name,
                "data": values,
                "row_count": len(values),
                "column_count": len(values[0]) if values else 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting sheet data: {str(e)}",
                "spreadsheet_id": spreadsheet_id,
                "sheet": sheet,
                "range": range_name
            }
    
    async def call_mcp_tool_with_service_account(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Alternative method: Call MCP tool with service account (if available)
        This would require setting up service account credentials
        """
        try:
            url = self._get_server_url()
            
            async with streamablehttp_client(url) as (read, write, _):
                async with ClientSession(read, write) as session:
                    # Initialize the connection
                    await session.initialize()
                    
                    # Call the tool
                    result = await session.call_tool(tool_name, parameters)
                    
                    # Parse the result
                    if result.isError:
                        return {
                            "success": False,
                            "error": result.content[0].text if result.content else "Unknown error"
                        }
                    else:
                        return {
                            "success": True,
                            "data": result.content[0].text if result.content else "No content"
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": f"MCP connection error: {str(e)}"
            }
    
    async def update_sheet_data(self, google_id: str, spreadsheet_id: str, sheet: str, range_name: str, values: list) -> Dict[str, Any]:
        """
        Update sheet data using user's OAuth credentials
        """
        try:
            # Get user tokens from database
            tokens = await get_user_tokens(google_id)
            if not tokens:
                return {"error": "User not authenticated"}
            
            # Create credentials
            credentials = Credentials(
                token=tokens['access_token'],
                refresh_token=tokens['refresh_token'],
                client_id=GOOGLE_CLIENT_ID,
                client_secret=GOOGLE_CLIENT_SECRET,
                token_uri="https://oauth2.googleapis.com/token",
                scopes=GOOGLE_SCOPES
            )
            
            from googleapiclient.discovery import build
            from google.auth.transport.requests import Request
            
            # Refresh token if needed
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                # Update tokens in database
                from app.database import save_user
                await save_user({
                    'google_id': google_id,
                    'access_token': credentials.token,
                    'refresh_token': credentials.refresh_token
                })
            
            # Build sheets service
            service = build('sheets', 'v4', credentials=credentials)
            
            # Update sheet data
            body = {'values': values}
            result = service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet}!{range_name}",
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            return {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "sheet": sheet,
                "range": range_name,
                "updated_cells": result.get('updatedCells', 0),
                "updated_rows": result.get('updatedRows', 0),
                "updated_columns": result.get('updatedColumns', 0)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error updating sheet data: {str(e)}",
                "spreadsheet_id": spreadsheet_id,
                "sheet": sheet,
                "range": range_name
            }
    
    async def create_new_sheet(self, google_id: str, spreadsheet_id: str, sheet_title: str) -> Dict[str, Any]:
        """
        Create a new sheet in the spreadsheet
        """
        try:
            # Get user tokens from database
            tokens = await get_user_tokens(google_id)
            if not tokens:
                return {"error": "User not authenticated"}
            
            # Create credentials
            credentials = Credentials(
                token=tokens['access_token'],
                refresh_token=tokens['refresh_token'],
                client_id=GOOGLE_CLIENT_ID,
                client_secret=GOOGLE_CLIENT_SECRET,
                token_uri="https://oauth2.googleapis.com/token",
                scopes=GOOGLE_SCOPES
            )
            
            from googleapiclient.discovery import build
            from google.auth.transport.requests import Request
            
            # Refresh token if needed
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                # Update tokens in database
                from app.database import save_user
                await save_user({
                    'google_id': google_id,
                    'access_token': credentials.token,
                    'refresh_token': credentials.refresh_token
                })
            
            # Build sheets service
            service = build('sheets', 'v4', credentials=credentials)
            
            # Create new sheet
            request_body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_title
                        }
                    }
                }]
            }
            
            result = service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=request_body
            ).execute()
            
            new_sheet = result['replies'][0]['addSheet']['properties']
            
            return {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "new_sheet": {
                    "sheet_id": new_sheet['sheetId'],
                    "title": new_sheet['title'],
                    "index": new_sheet['index']
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error creating new sheet: {str(e)}",
                "spreadsheet_id": spreadsheet_id,
                "sheet_title": sheet_title
            }

# Global MCP client instance
mcp_client = MCPGoogleSheetsClient()