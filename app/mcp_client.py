# app/mcp_client.py
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from urllib.parse import urlencode
import json
from typing import Optional, Dict, Any
from app.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_SCOPES
from app.database import get_user_tokens
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import re
from datetime import datetime
from calendar import month_name

# MCP Configuration
MCP_SERVER_URL = "https://server.smithery.ai/@SmartManoj/google-sheets-mcp/mcp"
MCP_API_KEY = "fe120802-bad4-4434-bec8-11c2af683af4" 
MCP_PROFILE = "incredible-firefly-hQK5C9"

def parse_range_start_row(range_name: str) -> int:
    """
    Parse a range string to extract the starting row number.
    Examples:
    - "A10:C100" -> 10
    - "B5:D20" -> 5  
    - "A1:Z1000" -> 1
    """
    try:
        # Match pattern like "A10:C100" or "B5:D20"
        match = re.match(r'^[A-Z]+(\d+):[A-Z]+\d+$', range_name.upper())
        if match:
            return int(match.group(1))
        
        # If no match, try to extract just the first number
        numbers = re.findall(r'\d+', range_name)
        if numbers:
            return int(numbers[0])
        
        # Default to 1 if can't parse
        return 1
    except (ValueError, AttributeError):
        return 1

def parse_cell_reference(cell_ref: str) -> tuple[str, int]:
    """
    Parse a cell reference to extract column and row.
    Examples:
    - "C3" -> ("C", 3)
    - "AA10" -> ("AA", 10)
    - "B1" -> ("B", 1)
    """
    try:
        # Match pattern like "C3", "AA10", etc.
        match = re.match(r'^([A-Z]+)(\d+)$', cell_ref.upper().strip())
        if match:
            column = match.group(1)
            row = int(match.group(2))
            return column, row
        
        # Default fallback
        return "A", 1
    except (ValueError, AttributeError):
        return "A", 1

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
            
            # Parse starting row number from range
            start_row = parse_range_start_row(range_name)
            
            # Transform data to include actual row indices and skip empty rows
            indexed_data = {}
            for i, row_data in enumerate(values):
                actual_row_number = start_row + i
                
                # Skip empty rows (rows with no data or only empty strings)
                if row_data and any(cell.strip() for cell in row_data if isinstance(cell, str)):
                    indexed_data[actual_row_number] = row_data
            
            return {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "sheet": sheet,
                "range": range_name,
                "data": indexed_data,
                "row_count": len(indexed_data),
                "column_count": len(values[0]) if values else 0,
                "total_rows_processed": len(values),
                "start_row": start_row
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting sheet data: {str(e)}",
                "spreadsheet_id": spreadsheet_id,
                "sheet": sheet,
                "range": range_name,
                "data": {},
                "row_count": 0,
                "column_count": 0,
                "total_rows_processed": 0,
                "start_row": parse_range_start_row(range_name)
            }
    
    async def get_column_data_with_user_auth(self, google_id: str, spreadsheet_id: str, sheet: str, cell_reference: str) -> Dict[str, Any]:
        """
        Get all data from a specific column starting from a given row using user's OAuth credentials.
        Stops when 10 consecutive empty rows are found.
        
        Args:
            google_id: User's Google ID
            spreadsheet_id: Google Sheets spreadsheet ID
            sheet: Sheet name (e.g., "Sheet1")
            cell_reference: Starting cell reference (e.g., "C3")
        
        Returns:
            Dict with indexed data: {row_number: [value], ...}
        """
        try:
            # Get user tokens from database
            tokens = await get_user_tokens(google_id)
            if not tokens:
                return {"error": "User not authenticated"}
            
            # Parse cell reference to get column and starting row
            column, start_row = parse_cell_reference(cell_reference)
            
            # Create credentials
            credentials = Credentials(
                token=tokens['access_token'],
                refresh_token=tokens['refresh_token'],
                client_id=GOOGLE_CLIENT_ID,
                client_secret=GOOGLE_CLIENT_SECRET,
                token_uri="https://oauth2.googleapis.com/token",
                scopes=GOOGLE_SCOPES
            )
            
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
            
            # Read open-ended range - NO ROW LIMIT!
            # Google Sheets API will read until the last row with data
            # Only stopping condition is 10 consecutive empty rows
            range_to_read = f"{column}{start_row}:{column}"
            
            # Get sheet data
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet}!{range_to_read}"
            ).execute()
            
            values = result.get('values', [])
            
            # Process data with 10 consecutive empty row stopping logic
            indexed_data = {}
            consecutive_empty_count = 0
            total_processed = 0
            
            for i, row_data in enumerate(values):
                actual_row_number = start_row + i
                total_processed += 1
                
                # Check if row is empty (no data or only empty/whitespace strings)
                is_empty = not row_data or not any(cell.strip() for cell in row_data if isinstance(cell, str))
                
                if is_empty:
                    consecutive_empty_count += 1
                    # Stop if we hit 10 consecutive empty rows
                    if consecutive_empty_count >= 100:
                        break
                else:
                    # Reset counter when we find non-empty data
                    consecutive_empty_count = 0
                    # Add non-empty row to results
                    indexed_data[actual_row_number] = row_data
            
            return {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "sheet": sheet,
                "cell_reference": cell_reference,
                "column": column,
                "start_row": start_row,
                "data": indexed_data,
                "row_count": len(indexed_data),
                "total_rows_processed": total_processed,
                "stopped_due_to_empty_rows": consecutive_empty_count >= 10
            }
            
        except Exception as e:
            column, start_row = parse_cell_reference(cell_reference)
            return {
                "success": False,
                "error": f"Error getting column data: {str(e)}",
                "spreadsheet_id": spreadsheet_id,
                "sheet": sheet,
                "cell_reference": cell_reference,
                "column": column,
                "start_row": start_row,
                "data": {},
                "row_count": 0,
                "total_rows_processed": 0,
                "stopped_due_to_empty_rows": False
            }

    async def get_col_values_from_range_real_indexing(self, google_id: str, spreadsheet_id: str, sheet: str, cell_reference: str) -> Dict[str, Any]:
        """
        Get all data from a specific column starting from a given row using user's OAuth credentials.
        Returns data with REAL Google Sheets row indices (not 0-based).
        Stops when 100 consecutive empty rows are found.
        
        Args:
            google_id: User's Google ID
            spreadsheet_id: Google Sheets spreadsheet ID
            sheet: Sheet name (e.g., "Sheet1")
            cell_reference: Starting cell reference (e.g., "C3")
        
        Returns:
            Dict with real indexed data: {real_row_number: [value], ...}
            Example: {10: ["Carpenter"], 11: ["Mason"], 15: ["Welder"]}
        """
        try:
            # Get user tokens from database
            tokens = await get_user_tokens(google_id)
            if not tokens:
                return {"error": "User not authenticated"}
            
            # Parse cell reference to get column and starting row
            column, start_row = parse_cell_reference(cell_reference)
            
            # Create credentials
            credentials = Credentials(
                token=tokens['access_token'],
                refresh_token=tokens['refresh_token'],
                client_id=GOOGLE_CLIENT_ID,
                client_secret=GOOGLE_CLIENT_SECRET,
                token_uri="https://oauth2.googleapis.com/token",
                scopes=GOOGLE_SCOPES
            )
            
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
            
            # Read a large range to capture all data (we'll process it to find the actual end)
            # Using 1000 rows should be sufficient for most use cases
            end_row = start_row + 999  # Read up to 1000 rows
            range_to_read = f"{column}{start_row}:{column}{end_row}"
            
            # Get sheet data
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet}!{range_to_read}"
            ).execute()
            
            values = result.get('values', [])
            
            # Process data with 100 consecutive empty row stopping logic
            # Keep REAL Google Sheets row indices (not 0-based)
            indexed_data = {}
            consecutive_empty_count = 0
            total_processed = 0
            
            for i, row_data in enumerate(values):
                real_row_number = start_row + i  # This is the actual Google Sheets row number
                total_processed += 1
                
                # Check if row is empty (no data or only empty/whitespace strings)
                is_empty = not row_data or not any(cell.strip() for cell in row_data if isinstance(cell, str))
                
                if is_empty:
                    consecutive_empty_count += 1
                    # Stop if we hit 100 consecutive empty rows
                    if consecutive_empty_count >= 100:
                        break
                else:
                    # Reset counter when we find non-empty data
                    consecutive_empty_count = 0
                    # Add non-empty row to results with REAL row number
                    indexed_data[real_row_number] = row_data
            
            return {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "sheet": sheet,
                "cell_reference": cell_reference,
                "column": column,
                "start_row": start_row,
                "data": indexed_data,  # This contains real Google Sheets row numbers as keys
                "row_count": len(indexed_data),
                "total_rows_processed": total_processed,
                "stopped_due_to_empty_rows": consecutive_empty_count >= 100
            }
            
        except Exception as e:
            column, start_row = parse_cell_reference(cell_reference)
            return {
                "success": False,
                "error": f"Error getting column data with real indexing: {str(e)}",
                "spreadsheet_id": spreadsheet_id,
                "sheet": sheet,
                "cell_reference": cell_reference,
                "column": column,
                "start_row": start_row,
                "data": {},
                "row_count": 0,
                "total_rows_processed": 0,
                "stopped_due_to_empty_rows": False
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
    
    async def get_row_values_from_range(self, google_id: str, spreadsheet_id: str, sheet: str, range_name: str) -> Dict[str, Any]:
        """
        Get row values from a specific range with column names as keys.
        
        Args:
            google_id: User's Google ID
            spreadsheet_id: Google Sheets spreadsheet ID
            sheet: Sheet name (e.g., "Sheet1")
            range_name: Range like "4A:4D" or "8AV:8BZ"
        
        Returns:
            Dict with column names as keys: {"A": data, "B": data, "C": data, ...}
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
            
            # Parse range to get column information first
            # Convert from "4A:4D" format to "A4:D4" format for Google Sheets API
            # Example: "4A:4D" -> row 4, columns A to D -> "A4:D4"
            # Example: "8AV:8BZ" -> row 8, columns AV to BZ -> "AV8:BZ8"
            range_match = re.match(r'^(\d+)([A-Z]+):(\d+)([A-Z]+)$', range_name.upper())
            if not range_match:
                return {
                    "success": False,
                    "error": f"Invalid range format: {range_name}. Expected format: '4A:4D' or '8AV:8BZ'",
                    "data": {}
                }
            
            start_row, start_col, end_row, end_col = range_match.groups()
            
            # Verify it's the same row
            if start_row != end_row:
                return {
                    "success": False,
                    "error": f"Range must be within the same row. Got row {start_row} to {end_row}",
                    "data": {}
                }
            
            # Convert to Google Sheets format: "A4:D4" instead of "4A:4D"
            google_sheets_range = f"{start_col}{start_row}:{end_col}{end_row}"
            
            # Get sheet data using the converted Google Sheets format
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet}!{google_sheets_range}"
            ).execute()
            
            values = result.get('values', [])
            
            # Generate column names from start_col to end_col
            def column_to_number(col):
                """Convert column letter(s) to number (A=1, B=2, ..., AA=27, etc.)"""
                result = 0
                for char in col:
                    result = result * 26 + (ord(char) - ord('A') + 1)
                return result
            
            def number_to_column(num):
                """Convert number to column letter(s) (1=A, 2=B, ..., 27=AA, etc.)"""
                result = ""
                while num > 0:
                    num -= 1
                    result = chr(num % 26 + ord('A')) + result
                    num //= 26
                return result
            
            start_col_num = column_to_number(start_col)
            end_col_num = column_to_number(end_col)
            
            # Create column-indexed data
            column_data = {}
            row_values = values[0] if values else []
            
            for i, col_num in enumerate(range(start_col_num, end_col_num + 1)):
                col_name = number_to_column(col_num)
                col_value = row_values[i] if i < len(row_values) else ""
                column_data[col_name] = col_value
            
            return {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "sheet": sheet,
                "range": range_name,  # Original format: "4A:4D"
                "row": int(start_row),
                "data": column_data,
                "column_count": len(column_data)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting row values: {str(e)}",
                "spreadsheet_id": spreadsheet_id,
                "sheet": sheet,
                "range": range_name,
                "data": {}
            }
    
    async def update_cells_with_operations(self, google_id: str, spreadsheet_id: str, sheet: str, cell_list: list, updation_list: list, type_list: list) -> Dict[str, Any]:
        """
        Update multiple cells with different operation types.
        
        Args:
            google_id: User's Google ID
            spreadsheet_id: Google Sheets spreadsheet ID
            sheet: Sheet name (e.g., "Sheet1")
            cell_list: List of cell references ["F10", "F15", "F20"]
            updation_list: List of numeric values [40.0, 0.0, 50.0]
            type_list: List of operation types ["add", "remove", "replace"]
        
        Operations:
            - "add": Add value to existing cell value
            - "remove": Set cell to zero (ignore updation value)
            - "replace": Replace cell value with new value
        
        Returns:
            Dict with success/failure status for each operation
        """
        try:
            # Validate input lists have same length
            if not (len(cell_list) == len(updation_list) == len(type_list)):
                return {
                    "success": False,
                    "error": "All input lists must have the same length",
                    "results": []
                }
            
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
            
            # Process each cell operation
            results = []
            successful_operations = 0
            
            for i, (cell_ref, update_value, operation_type) in enumerate(zip(cell_list, updation_list, type_list)):
                try:
                    # Validate operation type
                    if operation_type not in ["add", "remove", "replace"]:
                        results.append({
                            "cell": cell_ref,
                            "operation": operation_type,
                            "success": False,
                            "error": f"Invalid operation type: {operation_type}. Must be 'add', 'remove', or 'replace'"
                        })
                        continue
                    
                    # Convert update_value to float for validation
                    try:
                        update_value = float(update_value)
                    except (ValueError, TypeError):
                        results.append({
                            "cell": cell_ref,
                            "operation": operation_type,
                            "success": False,
                            "error": f"Update value must be numeric, got: {update_value}"
                        })
                        continue
                    
                    # Get current cell value for "add" operations
                    current_value = 0.0
                    if operation_type == "add":
                        try:
                            current_result = service.spreadsheets().values().get(
                                spreadsheetId=spreadsheet_id,
                                range=f"{sheet}!{cell_ref}"
                            ).execute()
                            
                            current_values = current_result.get('values', [[]])
                            if current_values and current_values[0]:
                                current_value = float(current_values[0][0]) if current_values[0][0] else 0.0
                        except (ValueError, TypeError):
                            # If current value is not numeric, treat as 0
                            current_value = 0.0
                    
                    # Calculate new value based on operation type
                    if operation_type == "add":
                        new_value = current_value + update_value
                    elif operation_type == "remove":
                        new_value = 0.0
                    elif operation_type == "replace":
                        new_value = update_value
                    
                    # Update the cell
                    update_result = service.spreadsheets().values().update(
                        spreadsheetId=spreadsheet_id,
                        range=f"{sheet}!{cell_ref}",
                        valueInputOption='USER_ENTERED',
                        body={'values': [[new_value]]}
                    ).execute()
                    
                    results.append({
                        "cell": cell_ref,
                        "operation": operation_type,
                        "success": True,
                        "old_value": current_value if operation_type == "add" else None,
                        "update_value": update_value,
                        "new_value": new_value,
                        "updated_cells": update_result.get('updatedCells', 0)
                    })
                    successful_operations += 1
                    
                except Exception as cell_error:
                    results.append({
                        "cell": cell_ref,
                        "operation": operation_type,
                        "success": False,
                        "error": f"Error updating cell: {str(cell_error)}"
                    })
            
            return {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "sheet": sheet,
                "total_operations": len(cell_list),
                "successful_operations": successful_operations,
                "failed_operations": len(cell_list) - successful_operations,
                "results": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error in batch cell update: {str(e)}",
                "spreadsheet_id": spreadsheet_id,
                "sheet": sheet,
                "results": []
            }
    
    async def log_update_operation(self, google_id: str, spreadsheet_id: str, site_engineer_name: str, phone_number: str, updated_row_index: str, updated_column_index: str, updated_value: str, updation_type: str, columns: str, user_query: str, feedback: str, sheet_name: str, operation_date: str = None) -> Dict[str, Any]:
        """
        Log update operations to a "LOG" sheet within the spreadsheet.
        Creates the LOG sheet if it doesn't exist.
        
        Args:
            google_id: User's Google ID
            spreadsheet_id: Google Sheets spreadsheet ID
            site_engineer_name: Engineer who made the update
            phone_number: Phone number of the engineer
            updated_row_index: Row that was updated
            updated_column_index: Column that was updated (e.g., "F", "G", "AA")
            updated_value: The new value that was set
            updation_type: Type of operation ("add", "remove", "replace")
            columns: Column information/header
            user_query: Original user query that triggered the update
            feedback: System/agent feedback about the operation
        
        Returns:
            Dict with success status and log entry details
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
            
            # Check if LOG sheet exists, create if not
            try:
                # Get spreadsheet metadata to check existing sheets
                spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
                sheets = spreadsheet.get('sheets', [])
                
                log_sheet_exists = False
                for sheet in sheets:
                    if sheet['properties']['title'] == 'LOG':
                        log_sheet_exists = True
                        break
                
                # Create LOG sheet if it doesn't exist
                if not log_sheet_exists:
                    # Create new sheet
                    request_body = {
                        'requests': [{
                            'addSheet': {
                                'properties': {
                                    'title': 'LOG'
                                }
                            }
                        }]
                    }
                    
                    service.spreadsheets().batchUpdate(
                        spreadsheetId=spreadsheet_id,
                        body=request_body
                    ).execute()
                    
                    # Add headers to the new LOG sheet
                    headers = [['Timestamp', 'Site Engineer', 'Phone Number', 'Row', 'Column', 'Value', 'Type', 'Operation Date', 'User Query', 'Feedback', 'Sheet Name']]
                    service.spreadsheets().values().update(
                        spreadsheetId=spreadsheet_id,
                        range='LOG!A1:K1',
                        valueInputOption='USER_ENTERED',
                        body={'values': headers}
                    ).execute()
                
            except Exception as sheet_error:
                return {
                    "success": False,
                    "error": f"Error creating/checking LOG sheet: {str(sheet_error)}"
                }
            
            # Get current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Use provided operation date or default to today
            if not operation_date:
                operation_date = datetime.now().strftime("%d-%m-%Y")
            
            # Prepare log entry
            log_entry = [
                timestamp,
                site_engineer_name,
                str(phone_number),
                str(updated_row_index),
                str(updated_column_index),
                str(updated_value),
                str(updation_type),
                str(operation_date),
                str(user_query),
                str(feedback),
                str(sheet_name)
            ]
            
            # Find next available row in LOG sheet
            try:
                # Get existing data to find next row
                existing_data = service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range='LOG!A:A'
                ).execute()
                
                existing_rows = existing_data.get('values', [])
                next_row = len(existing_rows) + 1
                
            except:
                # If error reading, assume it's row 2 (after headers)
                next_row = 2
            
            # Add log entry
            log_range = f'LOG!A{next_row}:K{next_row}'
            result = service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=log_range,
                valueInputOption='USER_ENTERED',
                body={'values': [log_entry]}
            ).execute()
            
            return {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "log_sheet": "LOG",
                "log_entry": {
                    "timestamp": timestamp,
                    "site_engineer": site_engineer_name,
                    "row": updated_row_index,
                    "column": updated_column_index,
                    "value": updated_value,
                    "type": updation_type,
                    "operation_date": operation_date,
                    "user_query": user_query,
                    "feedback": feedback
                },
                "log_row": next_row,
                "updated_cells": result.get('updatedCells', 0)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error logging operation: {str(e)}",
                "spreadsheet_id": spreadsheet_id
            }
    
    def get_days_in_month(self, month: str) -> int:
        """
        Get the number of days in a given month.
        
        Args:
            month: Month name (e.g., "JANUARY", "FEBRUARY")
            
        Returns:
            Number of days in the month
        """
        days_in_month = {
            'JANUARY': 31, 'FEBRUARY': 29, 'MARCH': 31, 'APRIL': 30,
            'MAY': 31, 'JUNE': 30, 'JULY': 31, 'AUGUST': 31,
            'SEPTEMBER': 30, 'OCTOBER': 31, 'NOVEMBER': 30, 'DECEMBER': 31
        }
        return days_in_month.get(month.upper(), 31)
    
    def get_column_letters_range(self, start_col: str, end_col: str) -> list[str]:
        """
        Generate a list of column letters from start to end.
        
        Args:
            start_col: Starting column (e.g., "P")
            end_col: Ending column (e.g., "AT")
            
        Returns:
            List of column letters
        """
        def column_to_number(col):
            result = 0
            for char in col:
                result = result * 26 + (ord(char) - ord('A') + 1)
            return result
        
        def number_to_column(num):
            result = ""
            while num > 0:
                num -= 1
                result = chr(num % 26 + ord('A')) + result
                num //= 26
            return result
        
        start_num = column_to_number(start_col)
        end_num = column_to_number(end_col)
        
        return [number_to_column(i) for i in range(start_num, end_num + 1)]
    
    async def populate_monthly_dates(self, google_id: str, spreadsheet_id: str, sheet_name: str, 
                                   month: str, year: int) -> Dict[str, Any]:
        """
        Populate monthly dates in the specified ranges and update headers.
        
        Args:
            google_id: User's Google ID
            spreadsheet_id: Target spreadsheet ID
            sheet_name: Sheet name (usually "DPR")
            month: Month name (e.g., "SEPTEMBER")
            year: Year (e.g., 2025)
            
        Returns:
            Dict with success status and update details
        """
        try:
            # Get user tokens
            tokens = await get_user_tokens(google_id)
            if not tokens:
                return {"success": False, "error": "User tokens not found"}
            
            # Create credentials
            credentials = Credentials(
                token=tokens['access_token'],
                refresh_token=tokens['refresh_token'],
                token_uri='https://oauth2.googleapis.com/token',
                client_id=GOOGLE_CLIENT_ID,
                client_secret=GOOGLE_CLIENT_SECRET,
                scopes=GOOGLE_SCOPES
            )
            
            # Build Sheets service
            service = build('sheets', 'v4', credentials=credentials)
            
            # Get days in month and generate dates
            days_in_month = self.get_days_in_month(month)
            month_num = str(datetime.strptime(month, "%B").month).zfill(2)
            
            # Generate date values for the month (clean format without prefix)
            date_values = []
            for day in range(1, days_in_month + 1):
                date_str = f"{day:02d}-{month_num}-{year}"
                date_values.append([date_str])
            
            # Add empty cells for remaining slots (up to 31 total)
            while len(date_values) < 31:
                date_values.append([""])
            
            # Get column ranges
            p_to_at_cols = self.get_column_letters_range("P", "AT")  # 31 columns
            av_to_bz_cols = self.get_column_letters_range("AV", "BZ")  # 31 columns
            
            # Prepare batch update requests
            requests = []
            
            # Update P8:AT8 with dates
            p_to_at_range = f"{sheet_name}!P8:AT8"
            requests.append({
                'range': p_to_at_range,
                'values': [date_values[i][0] for i in range(31)]
            })
            
            # Update AV8:BZ8 with dates (duplicate)
            av_to_bz_range = f"{sheet_name}!AV8:BZ8"
            requests.append({
                'range': av_to_bz_range,
                'values': [date_values[i][0] for i in range(31)]
            })
            
            # Update header text P7:AT7
            planned_header = f"Planned for Month of {month.upper()} {year}"
            p7_range = f"{sheet_name}!P7"
            requests.append({
                'range': p7_range,
                'values': [[planned_header]]
            })
            
            # Update header text AV7:BZ7
            achieved_header = f"ACHIEVED FOR month {month.upper()} {year}"
            av7_range = f"{sheet_name}!AV7"
            requests.append({
                'range': av7_range,
                'values': [[achieved_header]]
            })
            
            # Execute batch update (formatting applied first, so safe to use USER_ENTERED)
            batch_update_request = {
                'valueInputOption': 'USER_ENTERED',  # Normal input since formatting is pre-applied
                'data': [
                    {'range': p_to_at_range, 'values': [[date_values[i][0] for i in range(31)]]},
                    {'range': av_to_bz_range, 'values': [[date_values[i][0] for i in range(31)]]},
                    {'range': p7_range, 'values': [[planned_header]]},
                    {'range': av7_range, 'values': [[achieved_header]]}
                ]
            }
            
            # Find the sheet ID by name (case-insensitive) FIRST
            sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            target_sheet_id = None
            for sheet in sheet_metadata['sheets']:
                if sheet['properties']['title'].upper() == sheet_name.upper():
                    target_sheet_id = sheet['properties']['sheetId']
                    break
            
            # If sheet not found, use the first sheet
            if target_sheet_id is None and sheet_metadata['sheets']:
                target_sheet_id = sheet_metadata['sheets'][0]['properties']['sheetId']
            
            # Apply formatting FIRST to ensure proper text format
            if target_sheet_id is not None:
                # Apply formatting to ensure dates display properly as text and horizontal
                format_requests = [
                    {
                        "repeatCell": {
                            "range": {
                                "sheetId": target_sheet_id,
                                "startRowIndex": 7,  # Row 8 (0-indexed)
                                "endRowIndex": 8,
                                "startColumnIndex": 15,  # Column P (0-indexed) 
                                "endColumnIndex": 46     # Column AT+1 (0-indexed)
                            },
                            "cell": {
                                "userEnteredFormat": {
                                    "numberFormat": {
                                        "type": "TEXT",
                                        "pattern": "@"  # Force text format pattern
                                    },
                                "textRotation": {
                                    "angle": 90  # Vertical text (90 degrees)
                                },
                                "horizontalAlignment": "CENTER"
                                }
                            },
                            "fields": "userEnteredFormat(numberFormat,textRotation,horizontalAlignment)"
                        }
                    },
                    {
                        "repeatCell": {
                            "range": {
                                "sheetId": target_sheet_id,
                                "startRowIndex": 7,  # Row 8 (0-indexed)
                                "endRowIndex": 8,
                                "startColumnIndex": 47,  # Column AV (0-indexed)
                                "endColumnIndex": 78     # Column BZ+1 (0-indexed)
                            },
                            "cell": {
                                "userEnteredFormat": {
                                    "numberFormat": {
                                        "type": "TEXT",
                                        "pattern": "@"  # Force text format pattern
                                    },
                                "textRotation": {
                                    "angle": 90  # Vertical text (90 degrees)
                                },
                                "horizontalAlignment": "CENTER"
                                }
                            },
                            "fields": "userEnteredFormat(numberFormat,textRotation,horizontalAlignment)"
                        }
                    }
                ]
                
                # Apply formatting FIRST
                try:
                    format_result = service.spreadsheets().batchUpdate(
                        spreadsheetId=spreadsheet_id,
                        body={"requests": format_requests}
                    ).execute()
                except Exception as format_error:
                    # If formatting fails, continue without it
                    print(f"Warning: Could not apply formatting: {format_error}")
            
            # NOW insert the data with clean values
            result = service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=batch_update_request
            ).execute()
            
            return {
                "success": True,
                "month": month,
                "year": year,
                "days_populated": days_in_month,
                "empty_cells": 31 - days_in_month,
                "updated_ranges": [p_to_at_range, av_to_bz_range, p7_range, av7_range],
                "total_updates": result.get('totalUpdatedCells', 0),
                "formatting_applied": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error populating monthly dates: {str(e)}"
            }

    def get_previous_month_year(self, month: str, year: int) -> tuple[str, int]:
        """
        Get the previous month and year, handling year transitions.
        
        Args:
            month: Current month name (e.g., "JANUARY")
            year: Current year
            
        Returns:
            Tuple of (previous_month_name, previous_year)
        """
        month_names = [name.upper() for name in month_name[1:]]  # Skip empty first element
        
        try:
            current_month_index = month_names.index(month.upper())
            if current_month_index == 0:  # January
                previous_month = month_names[11]  # December
                previous_year = year - 1
            else:
                previous_month = month_names[current_month_index - 1]
                previous_year = year
            
            return previous_month, previous_year
        except ValueError:
            raise ValueError(f"Invalid month name: {month}")
    
    async def search_spreadsheet_by_name(self, google_id: str, spreadsheet_name: str) -> Dict[str, Any]:
        """
        Search for a spreadsheet by name in user's Google Drive.
        
        Args:
            google_id: User's Google ID
            spreadsheet_name: Name of the spreadsheet to search for
            
        Returns:
            Dict with success status and spreadsheet details
        """
        try:
            # Get user tokens
            tokens = await get_user_tokens(google_id)
            if not tokens:
                return {"success": False, "error": "User tokens not found"}
            
            # Create credentials
            credentials = Credentials(
                token=tokens['access_token'],
                refresh_token=tokens['refresh_token'],
                token_uri='https://oauth2.googleapis.com/token',
                client_id=GOOGLE_CLIENT_ID,
                client_secret=GOOGLE_CLIENT_SECRET,
                scopes=GOOGLE_SCOPES
            )
            
            # Build Drive service
            drive_service = build('drive', 'v3', credentials=credentials)
            
            # Search for spreadsheet by name
            query = f"name='{spreadsheet_name}' and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"
            results = drive_service.files().list(
                q=query,
                fields="files(id, name, createdTime, modifiedTime)"
            ).execute()
            
            files = results.get('files', [])
            
            # Log all found files for debugging
            print(f"Search query: {query}")
            print(f"Found {len(files)} files matching '{spreadsheet_name}':")
            for i, file in enumerate(files):
                print(f"  {i+1}. {file['name']} (ID: {file['id']}, Created: {file.get('createdTime')}, Modified: {file.get('modifiedTime')})")
            
            if files:
                # Return the first match (most recent if multiple)
                selected_file = files[0]
                print(f"Selected file: {selected_file['name']} (ID: {selected_file['id']})")
                return {
                    "success": True,
                    "found": True,
                    "spreadsheet_id": selected_file['id'],
                    "name": selected_file['name'],
                    "created_time": selected_file.get('createdTime'),
                    "modified_time": selected_file.get('modifiedTime')
                }
            else:
                return {
                    "success": True,
                    "found": False,
                    "message": f"No spreadsheet found with name: {spreadsheet_name}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error searching for spreadsheet: {str(e)}"
            }
    
    async def copy_spreadsheet(self, google_id: str, source_spreadsheet_id: str, new_name: str) -> Dict[str, Any]:
        """
        Create a copy of a spreadsheet with a new name.
        
        Args:
            google_id: User's Google ID
            source_spreadsheet_id: ID of the spreadsheet to copy
            new_name: Name for the new spreadsheet
            
        Returns:
            Dict with success status and new spreadsheet details
        """
        try:
            # Get user tokens
            tokens = await get_user_tokens(google_id)
            if not tokens:
                return {"success": False, "error": "User tokens not found"}
            
            # Create credentials
            credentials = Credentials(
                token=tokens['access_token'],
                refresh_token=tokens['refresh_token'],
                token_uri='https://oauth2.googleapis.com/token',
                client_id=GOOGLE_CLIENT_ID,
                client_secret=GOOGLE_CLIENT_SECRET,
                scopes=GOOGLE_SCOPES
            )
            
            # Build Drive service
            drive_service = build('drive', 'v3', credentials=credentials)
            
            # Copy the spreadsheet
            copy_request = {
                'name': new_name
            }
            
            # Log the copy operation details
            print(f"Copying spreadsheet - Source ID: {source_spreadsheet_id}, New name: {new_name}")
            
            copied_file = drive_service.files().copy(
                fileId=source_spreadsheet_id,
                body=copy_request
            ).execute()
            
            # Log the copy result
            print(f"Copy successful - New ID: {copied_file['id']}, New name: {copied_file['name']}")
            
            return {
                "success": True,
                "new_spreadsheet_id": copied_file['id'],
                "name": copied_file['name']
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error copying spreadsheet: {str(e)}"
            }
    
    async def copy_column_data(self, google_id: str, source_spreadsheet_id: str, target_spreadsheet_id: str, 
                              source_sheet: str, target_sheet: str, source_column: str, target_column: str, 
                              start_row: int = 10) -> Dict[str, Any]:
        """
        Copy data from one column to another column in different spreadsheets.
        
        Args:
            google_id: User's Google ID
            source_spreadsheet_id: Source spreadsheet ID
            target_spreadsheet_id: Target spreadsheet ID
            source_sheet: Source sheet name
            target_sheet: Target sheet name
            source_column: Source column (e.g., "N")
            target_column: Target column (e.g., "G")
            start_row: Starting row number (default: 10)
            
        Returns:
            Dict with success status and copy details
        """
        try:
            # Get user tokens
            tokens = await get_user_tokens(google_id)
            if not tokens:
                return {"success": False, "error": "User tokens not found"}
            
            # Create credentials
            credentials = Credentials(
                token=tokens['access_token'],
                refresh_token=tokens['refresh_token'],
                token_uri='https://oauth2.googleapis.com/token',
                client_id=GOOGLE_CLIENT_ID,
                client_secret=GOOGLE_CLIENT_SECRET,
                scopes=GOOGLE_SCOPES
            )
            
            # Build Sheets service
            service = build('sheets', 'v4', credentials=credentials)
            
            # Read data from source column (N10 to end of data)
            source_range = f"{source_sheet}!{source_column}{start_row}:{source_column}"
            source_result = service.spreadsheets().values().get(
                spreadsheetId=source_spreadsheet_id,
                range=source_range
            ).execute()
            
            source_values = source_result.get('values', [])
            
            if not source_values:
                return {
                    "success": True,
                    "data_copied": False,
                    "message": f"No data found in {source_column}{start_row} onwards",
                    "rows_copied": 0
                }
            
            # Write data to target column (G10 onwards)
            target_range = f"{target_sheet}!{target_column}{start_row}:{target_column}{start_row + len(source_values) - 1}"
            
            update_result = service.spreadsheets().values().update(
                spreadsheetId=target_spreadsheet_id,
                range=target_range,
                valueInputOption='USER_ENTERED',
                body={'values': source_values}
            ).execute()
            
            return {
                "success": True,
                "data_copied": True,
                "rows_copied": len(source_values),
                "source_range": source_range,
                "target_range": target_range,
                "updated_cells": update_result.get('updatedCells', 0)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error copying column data: {str(e)}"
            }
    
    async def get_log_data(self, google_id: str, spreadsheet_id: str) -> Dict[str, Any]:
        """
        Retrieve all log data from the LOG sheet.
        Returns data as list of lists (without headers) for LLM processing.
        
        Args:
            google_id: User's Google ID
            spreadsheet_id: Google Sheets spreadsheet ID
        
        Returns:
            Dict with log data as list of lists
        """
        try:
            # Get user tokens from database
            tokens = await get_user_tokens(google_id)
            if not tokens:
                return {"success": False, "error": "User not authenticated", "data": [], "logs_processed": 0}
            
            # Create credentials
            credentials = Credentials(
                token=tokens['access_token'],
                refresh_token=tokens['refresh_token'],
                client_id=GOOGLE_CLIENT_ID,
                client_secret=GOOGLE_CLIENT_SECRET,
                token_uri="https://oauth2.googleapis.com/token",
                scopes=GOOGLE_SCOPES
            )
            
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
            
            # Get all log data (skip header row)
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range='LOG!A2:K1000'  # Start from row 2 to skip headers, up to 1000 rows
            ).execute()
            
            values = result.get('values', [])
            
            # Filter out empty rows and convert to proper format
            log_data = []
            for row in values:
                # Ensure row has all 11 columns, pad with empty strings if needed
                while len(row) < 11:
                    row.append('')
                
                # Only add non-empty rows (at least timestamp should exist)
                if row[0].strip():  # Check if timestamp exists
                    log_data.append(row)
            
            return {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "data": log_data,
                "logs_processed": len(log_data)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error retrieving log data: {str(e)}",
                "spreadsheet_id": spreadsheet_id,
                "data": [],
                "logs_processed": 0
            }
    
    async def check_dpr_format_sheet_exists(self, google_id: str) -> Dict[str, Any]:
        """
        Check if a spreadsheet named "DPR_FORMAT" exists in the user's Google Drive.
        
        Args:
            google_id: User's Google ID
        
        Returns:
            Dict with success status and sheet details if found
        """
        try:
            # Get user tokens
            tokens = await get_user_tokens(google_id)
            if not tokens:
                return {"success": False, "error": "User tokens not found"}
            
            # Create credentials
            credentials = Credentials(
                token=tokens['access_token'],
                refresh_token=tokens['refresh_token'],
                token_uri='https://oauth2.googleapis.com/token',
                client_id=GOOGLE_CLIENT_ID,
                client_secret=GOOGLE_CLIENT_SECRET,
                scopes=GOOGLE_SCOPES
            )
            
            # Build Drive service
            drive_service = build('drive', 'v3', credentials=credentials)
            
            # Search for DPR_FORMAT spreadsheet
            query = "name='DPR_FORMAT' and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"
            results = drive_service.files().list(
                q=query,
                fields="files(id, name, createdTime, modifiedTime, webViewLink)"
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                # Return the first match
                return {
                    "success": True,
                    "exists": True,
                    "spreadsheet_id": files[0]['id'],
                    "name": files[0]['name'],
                    "created_time": files[0].get('createdTime'),
                    "modified_time": files[0].get('modifiedTime'),
                    "web_view_link": files[0].get('webViewLink')
                }
            else:
                return {
                    "success": True,
                    "exists": False,
                    "message": "DPR_FORMAT spreadsheet not found"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error checking for DPR_FORMAT sheet: {str(e)}"
            }
    
    async def upload_dpr_format_sheet(self, google_id: str) -> Dict[str, Any]:
        """
        Upload the DPR_FORMAT.xlsx file to the user's Google Drive.
        
        Args:
            google_id: User's Google ID
        
        Returns:
            Dict with success status and uploaded file details
        """
        try:
            import os
            from googleapiclient.http import MediaFileUpload
            
            # Get user tokens
            tokens = await get_user_tokens(google_id)
            if not tokens:
                return {"success": False, "error": "User tokens not found"}
            
            # Create credentials
            credentials = Credentials(
                token=tokens['access_token'],
                refresh_token=tokens['refresh_token'],
                token_uri='https://oauth2.googleapis.com/token',
                client_id=GOOGLE_CLIENT_ID,
                client_secret=GOOGLE_CLIENT_SECRET,
                scopes=GOOGLE_SCOPES
            )
            
            # Build Drive service
            drive_service = build('drive', 'v3', credentials=credentials)
            
            # Check if file exists
            file_path = os.path.join(os.path.dirname(__file__), 'templates', 'DPR_FORMAT.xlsx')
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"DPR_FORMAT.xlsx file not found at {file_path}"
                }
            
            # Prepare file metadata
            file_metadata = {
                'name': 'DPR_FORMAT',
                'mimeType': 'application/vnd.google-apps.spreadsheet'
            }
            
            # Prepare media upload
            media = MediaFileUpload(
                file_path,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                resumable=True
            )
            
            # Upload the file
            file = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,createdTime,modifiedTime,webViewLink'
            ).execute()
            
            return {
                "success": True,
                "spreadsheet_id": file.get('id'),
                "name": file.get('name'),
                "created_time": file.get('createdTime'),
                "modified_time": file.get('modifiedTime'),
                "web_view_link": file.get('webViewLink'),
                "message": "DPR_FORMAT spreadsheet uploaded successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error uploading DPR_FORMAT sheet: {str(e)}"
            }

# Global MCP client instance
mcp_client = MCPGoogleSheetsClient()