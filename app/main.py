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
from app.models import TokenResponse, WriteResponse, DocumentListResponse, SheetDataResponse, ColumnDataResponse, UpdatedSheetRequest, UpdatedSheetResponse, DPRUpdationResult, RowDataResponse, CopySpreadsheetRequest, CopySpreadsheetResponse, DLRUpdationResult, UpdatedDLRRequest, UpdatedDLRResponse
from app.mcp_client import mcp_client
from app.llm_response import get_support_agent, get_dlr_support_agent, prompt_builder, prompt_builder_for_dlr_updation
from app.fuzzy_matching import get_best_fuzzy_matches
from app.config import GROQ_API_KEY
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
                    <li><strong>GET /mcp/column-data/{sheet_id}</strong> - Get entire column data from a starting cell (e.g., C3)</li>
                    <li><strong>GET /mcp/row-data/{sheet_id}</strong> - Get row data with column names as keys (e.g., 4A:4D)</li>
                    <li><strong>POST /update_dpr/{sheet_id}</strong> - Process DPR updates using AI analysis</li>
                    <li><strong>POST /update-dlr/{sheet_id}</strong> - Process DLR updates with fuzzy matching and AI analysis</li>
                    <li><strong>POST /new-spreadsheet</strong> - Copy spreadsheet with monthly naming and previous month data transfer</li>
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

@app.get("/mcp/sheet-data/{sheet_id}", response_model=SheetDataResponse)
async def get_sheet_data_mcp(
    sheet_id: str,
    sheet: str = "Sheet1",
    range_name: str = "A1:Z1000",
    current_user: dict = Depends(get_current_user)
):
    """
    Get sheet data using MCP integration with user's OAuth credentials.
    This endpoint uses 0-based indexing instead of actual Google Sheets row numbers.
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
        
        # Convert to 0-based indexing
        original_data = result.get('data', {})
        zero_indexed_data = {}
        
        # Convert from actual row numbers to 0-based index
        for index, (row_num, row_data) in enumerate(original_data.items()):
            zero_indexed_data[index] = row_data
        
        # Update the result with 0-based indexed data
        result['data'] = zero_indexed_data
        result['row_count'] = len(zero_indexed_data)
        
        return SheetDataResponse(**result)
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MCP error: {str(e)}")

@app.get("/mcp/column-data/{sheet_id}", response_model=ColumnDataResponse)
async def get_column_data_mcp(
    sheet_id: str,
    cell_reference: str,
    sheet: str = "Sheet1",
    current_user: dict = Depends(get_current_user)
):
    """
    Get all data from a specific column starting from a given row using MCP integration.
    Stops reading when 10 consecutive empty rows are encountered.
    
    Args:
        sheet_id: Google Sheets spreadsheet ID
        cell_reference: Starting cell reference (e.g., "C3" for column C starting from row 3)
        sheet: Sheet name (default: "Sheet1")
        
    Returns:
        Column data with actual row indices: {row_number: [value], ...}
        
    Example:
        GET /mcp/column-data/1ABC123.../C3?sheet=Sheet1
        Returns: {3: ["data1"], 5: ["data2"], 7: ["data3"], ...}
    """
    try:
        result = await mcp_client.get_column_data_with_user_auth(
            google_id=current_user['google_id'],
            spreadsheet_id=sheet_id,
            sheet=sheet,
            cell_reference=cell_reference
        )
        
        if not result.get('success', False):
            raise HTTPException(status_code=500, detail=result.get('error', 'Unknown error'))
        
        return ColumnDataResponse(**result)
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MCP column data error: {str(e)}")

@app.get("/mcp/row-data/{sheet_id}", response_model=RowDataResponse)
async def get_row_data_mcp(
    sheet_id: str,
    range_name: str,
    sheet: str = "Sheet1",
    current_user: dict = Depends(get_current_user)
):
    """
    Get row data from a specific range with column names as keys using MCP integration.
    
    Args:
        sheet_id: Google Sheets spreadsheet ID
        range_name: Range in format "RowColumn:RowColumn" like "4A:4D" or "8AV:8BZ" 
                   (single row with column range - row number first, then column letters)
        sheet: Sheet name (default: "Sheet1")
        
    Returns:
        Row data with column names as keys: {"A": data, "B": data, "C": data, ...}
        
    Examples:
        GET /mcp/row-data/1ABC123.../4A:4D?sheet=Sheet1
        Returns row 4, columns A to D: {"A": "data1", "B": "data2", "C": "data3", "D": "data4"}
        
        GET /mcp/row-data/1ABC123.../8AV:8BZ?sheet=Sheet1  
        Returns row 8, columns AV to BZ: {"AV": "data1", "AW": "data2", ..., "BZ": "data31"}
    """
    try:
        result = await mcp_client.get_row_values_from_range(
            google_id=current_user['google_id'],
            spreadsheet_id=sheet_id,
            sheet=sheet,
            range_name=range_name
        )
        
        if not result.get('success', False):
            raise HTTPException(status_code=500, detail=result.get('error', 'Unknown error'))
        
        return RowDataResponse(**result)
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MCP row data error: {str(e)}")

@app.post("/update-dpr/{sheet_id}", response_model=UpdatedSheetResponse)
async def update_dpr(
    sheet_id: str,
    request: UpdatedSheetRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Process sheet data through LLM for DPR updates and perform actual cell updates.
    
    This endpoint:
    1. Gets element data from column B starting at row 10
    2. Gets activity data from range C10:E96  
    3. Combines data with user query using prompt builder
    4. Processes through LLM for structured analysis
    5. Gets date-column mapping from row 8AV:8BZ
    6. Calculates target cells (element_index + activity_index)
    7. Performs actual cell updates in the spreadsheet
    8. Logs all update operations to LOG sheet
    
    Args:
        sheet_id: Google Sheets spreadsheet ID
        request: Contains site_engineer_name, phone_number, users_query
        
    Returns:
        Structured response with LLM analysis, update results, and agent feedback
        
    Example Flow:
        - User: "Villa 101 Excavation done by 40 cubic meter on 8 August 2025"
        - LLM: element_index=[10], activity_index=[1], quantities=[[40, "add"]], date="08-08-2025"
        - System: Finds column "BC" for date "08-08-2025", updates cell BC11 (10+1) with +40
        - Logs: Records operation in LOG sheet with all details
    """
    try:
        # Get element data from column B starting at B10
        element_result = await mcp_client.get_column_data_with_user_auth(
            google_id=current_user['google_id'],
            spreadsheet_id=sheet_id,
            sheet="DPR",
            cell_reference="B10"
        )
        
        if not element_result.get('success', False):
            raise HTTPException(status_code=500, detail=f"Failed to get element data: {element_result.get('error', 'Unknown error')}")
        
        # Get activity data from range C10:E96
        activity_result = await mcp_client.get_sheet_data_with_user_auth(
            google_id=current_user['google_id'],
            spreadsheet_id=sheet_id,
            sheet="DPR",
            range_name="C10:E96"
        )
        
        if not activity_result.get('success', False):
            raise HTTPException(status_code=500, detail=f"Failed to get activity data: {activity_result.get('error', 'Unknown error')}")
        
        # Convert activity data to 0-based indexing (same as /mcp/sheet-data endpoint)
        original_activity_data = activity_result.get('data', {})
        zero_indexed_activity_data = {}
        
        # Convert from actual row numbers to 0-based index for activity data
        for index, (row_num, row_data) in enumerate(original_activity_data.items()):
            zero_indexed_activity_data[index] = row_data
        
        # Convert data to string format for prompt
        element_data_str = str(element_result.get('data', {}))
        activity_data_str = str(zero_indexed_activity_data)
        
        # Build prompt using the prompt builder
        prompt = prompt_builder(
            element_data=element_data_str,
            activity_data=activity_data_str,
            users_query=request.users_query
        )
        
        # Get LLM agent and process the prompt
        if not GROQ_API_KEY:
            raise HTTPException(status_code=500, detail="Groq API key not configured")
        
        try:
            agent = get_support_agent(GROQ_API_KEY)
            run_response = agent.run(prompt)
            
            # Extract the actual result from RunResponse
            # The agent should return a DPRUpdationResult directly, but it's wrapped in RunResponse
            if hasattr(run_response, 'content'):
                llm_response = run_response.content
            elif hasattr(run_response, 'data'):
                llm_response = run_response.data
            else:
                # If it's already the right type, use it directly
                llm_response = run_response
                
            # Validate that we have a proper DPRUpdationResult
            if not isinstance(llm_response, DPRUpdationResult):
                # Try to create one from the response if it's a dict
                if isinstance(llm_response, dict):
                    llm_response = DPRUpdationResult(**llm_response)
                else:
                    raise ValueError(f"Invalid LLM response type: {type(llm_response)}")
                    
        except Exception as llm_error:
            raise HTTPException(status_code=500, detail=f"LLM processing error: {str(llm_error)}")
        
        # Validate operation date
        operation_date = llm_response.operation_date
        if operation_date:
            # Validate date format and check if it's not in the future
            try:
                from datetime import datetime
                if operation_date:  # Not empty string
                    parsed_date = datetime.strptime(operation_date, "%d-%m-%Y")
                    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    
                    if parsed_date > today:
                        # Future date detected, use today's date
                        operation_date = datetime.now().strftime("%d-%m-%Y")
                        # Update the LLM response
                        llm_response.operation_date = operation_date
                        # Update feedback to mention date correction
                        if llm_response.agent_feedback:
                            llm_response.agent_feedback[0] += " (Note: Future date corrected to today's date)"
            except ValueError:
                # Invalid date format, use today's date
                operation_date = datetime.now().strftime("%d-%m-%Y")
                llm_response.operation_date = operation_date
        
        # Perform actual cell updates if LLM provided valid data
        update_summary = "No updates performed"
        if (llm_response.element_index and llm_response.activity_index and 
            llm_response.activity_quantities and llm_response.operation_date):
            
            try:
                # Get date-column mapping from row 8AV:8BZ
                date_mapping_result = await mcp_client.get_row_values_from_range(
                    google_id=current_user['google_id'],
                    spreadsheet_id=sheet_id,
                    sheet="DPR",
                    range_name="8AV:8BZ"
                )
                
                if not date_mapping_result.get('success', False):
                    raise HTTPException(status_code=500, detail=f"Failed to get date mapping: {date_mapping_result.get('error', 'Unknown error')}")
                
                # Find the column that matches the operation date
                date_data = date_mapping_result.get('data', {})
                target_column = None
                
                for column, date_value in date_data.items():
                    if date_value == llm_response.operation_date:
                        target_column = column
                        break
                
                if not target_column:
                    raise HTTPException(status_code=400, detail=f"No column found for date: {llm_response.operation_date}")
                
                # Calculate target cells and prepare updates
                cell_list = []
                updation_list = []
                type_list = []
                
                for i in range(len(llm_response.element_index)):
                    # Calculate row: element_index + activity_index
                    element_idx = int(llm_response.element_index[i])
                    activity_idx = int(llm_response.activity_index[i])
                    target_row = element_idx + activity_idx
                    
                    # Create cell reference (e.g., "BC11", "BC98")
                    cell_ref = f"{target_column}{target_row}"
                    cell_list.append(cell_ref)
                    
                    # Extract quantity and operation type
                    quantity_str, operation_type = llm_response.activity_quantities[i]
                    updation_list.append(float(quantity_str))
                    type_list.append(operation_type)
                
                # Perform batch cell updates
                update_result = await mcp_client.update_cells_with_operations(
                    google_id=current_user['google_id'],
                    spreadsheet_id=sheet_id,
                    sheet="DPR",
                    cell_list=cell_list,
                    updation_list=updation_list,
                    type_list=type_list
                )
                
                if not update_result.get('success', False):
                    raise HTTPException(status_code=500, detail=f"Failed to update cells: {update_result.get('error', 'Unknown error')}")
                
                # Log each update operation
                for i, result in enumerate(update_result.get('results', [])):
                    if result.get('success', False):
                        # Extract row number correctly from cell reference
                        element_idx = int(llm_response.element_index[i])
                        activity_idx = int(llm_response.activity_index[i])
                        calculated_row = element_idx + activity_idx
                        
                        await mcp_client.log_update_operation(
                            google_id=current_user['google_id'],
                            spreadsheet_id=sheet_id,
                            site_engineer_name=request.site_engineer_name,
                            phone_number=request.phone_number,  # Add phone number
                            updated_row_index=str(calculated_row),  # Use calculated row directly
                            updated_column_index=target_column,
                            updated_value=str(result.get('new_value', updation_list[i])),
                            updation_type=type_list[i],
                            columns=target_column,
                            user_query=request.users_query,
                            feedback=llm_response.agent_feedback[0] if llm_response.agent_feedback else "Update completed",
                            sheet_name="DPR",  # Always use DPR for this endpoint
                            operation_date=llm_response.operation_date
                        )
                
                successful_updates = update_result.get('successful_operations', 0)
                total_updates = update_result.get('total_operations', 0)
                update_summary = f"Updated {successful_updates}/{total_updates} cells successfully"
                
            except HTTPException as e:
                raise e
            except Exception as update_error:
                raise HTTPException(status_code=500, detail=f"Cell update error: {str(update_error)}")
        
        # Create summary strings for the response
        element_summary = f"Column B data from row 10: {len(element_result.get('data', {}))} rows retrieved"
        activity_summary = f"Range C10:E96 data (0-indexed): {len(zero_indexed_activity_data)} rows retrieved"
        
        return UpdatedSheetResponse(
            success=True,
            site_engineer_name=request.site_engineer_name,
            phone_number=request.phone_number,
            sheet_id=sheet_id,
            sheet_name="DPR",
            users_query=request.users_query,
            element_data_summary=element_summary,
            activity_data_summary=f"{activity_summary}. {update_summary}",
            llm_result=llm_response
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        return UpdatedSheetResponse(
            success=False,
            site_engineer_name=request.site_engineer_name,
            phone_number=request.phone_number,
            sheet_id=sheet_id,
            sheet_name="DPR",
            users_query=request.users_query,
            element_data_summary="Failed to retrieve",
            activity_data_summary="Failed to retrieve", 
            llm_result=None,
            error=f"Processing error: {str(e)}"
        )

@app.post("/update-dlr/{sheet_id}", response_model=UpdatedDLRResponse)
async def update_dlr(
    sheet_id: str,
    request: UpdatedDLRRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Process DLR sheet data through LLM for updates and perform actual cell updates.
    
    This endpoint:
    1. Gets column data from 8A in DLR sheet using real indexing
    2. Gets row data from range 6A:6ZZ in DLR sheet
    3. Runs fuzzy matching on both datasets separately using user query
    4. Combines fuzzy matching results with user query using prompt builder for DLR
    5. Processes through LLM for structured analysis
    6. Performs direct cell updates using columns_index[i] + row_index[i] pattern
    7. Logs all update operations to LOG sheet
    
    Args:
        sheet_id: Google Sheets spreadsheet ID
        request: Contains site_engineer_name, phone_number, users_query
        
    Returns:
        Structured response with LLM analysis, update results, and feedback
        
    Example Flow:
        - User: "Grinder for Villa 101 has been done for 100 labors"
        - LLM: row_index=["D"], columns_index=["14"], quantities=[100] (may return swapped)
        - System: Auto-detects correct format → Updates cell D14 with +100 (add operation)
        - Logs: Records operations in LOG sheet with all details
    """
    try:
        # Step 1: Get column data from 8A using real indexing
        column_result = await mcp_client.get_col_values_from_range_real_indexing(
            google_id=current_user['google_id'],
            spreadsheet_id=sheet_id,
            sheet="DLR",
            cell_reference="8A"
        )
        
        if not column_result.get('success', False):
            raise HTTPException(status_code=500, detail=f"Failed to get column data: {column_result.get('error', 'Unknown error')}")
        
        # Step 2: Get row data from range 6A:6ZZ
        row_result = await mcp_client.get_row_values_from_range(
            google_id=current_user['google_id'],
            spreadsheet_id=sheet_id,
            sheet="DLR",
            range_name="6A:6ZZ"
        )
        
        if not row_result.get('success', False):
            raise HTTPException(status_code=500, detail=f"Failed to get row data: {row_result.get('error', 'Unknown error')}")
        
        # Step 3: Run fuzzy matching on both datasets separately
        
        # Fuzzy matching for column data (convert to format expected by fuzzy matching)
        column_data = column_result.get('data', {})
        column_search_dict = {}
        for row_num, row_data in column_data.items():
            if row_data and len(row_data) > 0:
                column_search_dict[str(row_num)] = row_data[0]  # Take first element from list
        
        column_fuzzy_matches = get_best_fuzzy_matches(request.users_query, column_search_dict, limit=10)
        
        # Fuzzy matching for row data 
        row_data = row_result.get('data', {})
        row_fuzzy_matches = get_best_fuzzy_matches(request.users_query, row_data, limit=10)
        
        # Step 4: Build prompt using fuzzy matching results
        column_matches_str = str(column_fuzzy_matches)
        row_matches_str = str(row_fuzzy_matches)
        
        prompt = prompt_builder_for_dlr_updation(
            column_name=column_matches_str,
            row_data=row_matches_str,
            users_query=request.users_query
        )
        
        # Step 5: Get LLM agent and process the prompt
        if not GROQ_API_KEY:
            raise HTTPException(status_code=500, detail="Groq API key not configured")
        
        try:
            agent = get_dlr_support_agent(GROQ_API_KEY)
            run_response = agent.run(prompt)
            
            # Extract the actual result from RunResponse
            if hasattr(run_response, 'content'):
                llm_response = run_response.content
            elif hasattr(run_response, 'data'):
                llm_response = run_response.data
            else:
                llm_response = run_response
                
            # Validate that we have a proper DLRUpdationResult
            if not isinstance(llm_response, DLRUpdationResult):
                if isinstance(llm_response, dict):
                    llm_response = DLRUpdationResult(**llm_response)
                else:
                    raise ValueError(f"Invalid LLM response type: {type(llm_response)}")
                    
        except Exception as llm_error:
            raise HTTPException(status_code=500, detail=f"LLM processing error: {str(llm_error)}")
        
        # Step 6: Perform actual cell updates using direct column + row pattern
        update_summary = "No updates performed"
        if (llm_response.row_index and llm_response.columns_index and llm_response.quantities):
            
            try:
                # Prepare cell updates using columns_index[i] + row_index[i] pattern
                cell_list = []
                updation_list = []
                type_list = []
                
                for i in range(len(llm_response.row_index)):
                    # Direct cell reference: columns_index[i] + row_index[i]
                    # Note: LLM might return them in wrong order, so we need to check which is numeric
                    col_val = llm_response.columns_index[i]
                    row_val = llm_response.row_index[i]
                    
                    # Determine correct cell reference - column should be letters, row should be numbers
                    if col_val.isdigit() and not row_val.isdigit():
                        # LLM returned them swapped: columns_index is numeric, row_index is letters
                        # Correct format: row_val (letters) + col_val (numbers) = like "D14"
                        cell_ref = f"{row_val}{col_val}"
                    elif not col_val.isdigit() and row_val.isdigit():
                        # Correct format: columns_index is letters, row_index is numbers = like "S10"
                        cell_ref = f"{col_val}{row_val}"
                    else:
                        # Fallback to original format if unclear
                        cell_ref = f"{col_val}{row_val}"
                    
                    cell_list.append(cell_ref)
                    
                    # Use quantity directly with add operation for DLR
                    updation_list.append(float(llm_response.quantities[i]))
                    type_list.append("add")  # Use add operation for DLR to increment values
                
                # Perform batch cell updates
                update_result = await mcp_client.update_cells_with_operations(
                    google_id=current_user['google_id'],
                    spreadsheet_id=sheet_id,
                    sheet="DLR",
                    cell_list=cell_list,
                    updation_list=updation_list,
                    type_list=type_list
                )
                
                if not update_result.get('success', False):
                    raise HTTPException(status_code=500, detail=f"Failed to update cells: {update_result.get('error', 'Unknown error')}")
                
                # Step 7: Log each update operation
                for i, result in enumerate(update_result.get('results', [])):
                    if result.get('success', False):
                        # Fix row/column values for logging - use the corrected cell reference
                        col_val = llm_response.columns_index[i]
                        row_val = llm_response.row_index[i]
                        
                        # Determine correct row and column for logging
                        if col_val.isdigit() and not row_val.isdigit():
                            # LLM returned them swapped - correct for logging
                            log_row_index = col_val  # The numeric value is the row
                            log_column_index = row_val  # The letter value is the column
                        elif not col_val.isdigit() and row_val.isdigit():
                            # Correct format
                            log_row_index = row_val  # The numeric value is the row
                            log_column_index = col_val  # The letter value is the column
                        else:
                            # Fallback - use as provided
                            log_row_index = row_val
                            log_column_index = col_val
                        
                        await mcp_client.log_update_operation(
                            google_id=current_user['google_id'],
                            spreadsheet_id=sheet_id,
                            site_engineer_name=request.site_engineer_name,
                            phone_number=request.phone_number,
                            updated_row_index=log_row_index,  # Corrected row (numeric)
                            updated_column_index=log_column_index,  # Corrected column (letter)
                            updated_value=str(result.get('new_value', updation_list[i])),
                            updation_type=type_list[i],
                            columns=log_column_index,
                            user_query=request.users_query,
                            feedback=llm_response.feedbacks[0] if llm_response.feedbacks else "DLR update completed",
                            sheet_name="DLR",  # Add sheet name
                            operation_date=""  # No date handling for DLR
                        )
                
                successful_updates = update_result.get('successful_operations', 0)
                total_updates = update_result.get('total_operations', 0)
                update_summary = f"Updated {successful_updates}/{total_updates} cells successfully"
                
            except HTTPException as e:
                raise e
            except Exception as update_error:
                raise HTTPException(status_code=500, detail=f"Cell update error: {str(update_error)}")
        
        # Create summary strings for the response
        column_summary = f"Column data from 8A (real indexing): {len(column_data)} rows retrieved. Fuzzy matches: {len(column_fuzzy_matches)}"
        row_summary = f"Row data from 6A:6ZZ: {row_result.get('column_count', 0)} columns retrieved. Fuzzy matches: {len(row_fuzzy_matches)}. {update_summary}"
        
        return UpdatedDLRResponse(
            success=True,
            site_engineer_name=request.site_engineer_name,
            phone_number=request.phone_number,
            sheet_id=sheet_id,
            users_query=request.users_query,
            column_data_summary=column_summary,
            row_data_summary=row_summary,
            llm_result=llm_response
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        return UpdatedDLRResponse(
            success=False,
            site_engineer_name=request.site_engineer_name,
            phone_number=request.phone_number,
            sheet_id=sheet_id,
            users_query=request.users_query,
            column_data_summary="Failed to retrieve",
            row_data_summary="Failed to retrieve", 
            llm_result=None,
            error=f"Processing error: {str(e)}"
        )

@app.post("/new-spreadsheet", response_model=CopySpreadsheetResponse)
async def new_spreadsheet_endpoint(
    request: CopySpreadsheetRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a copy of a spreadsheet with monthly naming format, populate dates, and copy data from previous month.
    
    This endpoint:
    1. Creates a copy of the source spreadsheet
    2. Names it with format: {project_name}_{month}_{current_year}
    3. Populates monthly dates in P8:AT8 and AV8:BZ8 (DD-MM-YYYY format)
    4. Updates headers P7:AT7 ("Planned for Month of {MONTH} {YEAR}") and AV7:BZ7 ("ACHIEVED FOR month {MONTH} {YEAR}")
    5. Searches for previous month's spreadsheet by name
    6. Copies data from previous month's N10:end to new spreadsheet's G10:end (DPR sheet only)
    
    Date Population Rules:
    - 31-day months: Fill all 31 cells (Jan, Mar, May, Jul, Aug, Oct, Dec)
    - 30-day months: Fill 30 cells, leave 1 empty (Apr, Jun, Sep, Nov)  
    - February: Fill 29 cells, leave 2 empty (always 29 days)
    
    Args:
        request: Contains spreadsheet_id (source), project_name, month
        
    Returns:
        Response with new spreadsheet details, date population status, and data copy status
        
    Example:
        - Input: project_name="NEST", month="SEPTEMBER"
        - Creates: "NEST_SEPTEMBER_2025"
        - Dates: 01-09-2025 to 30-09-2025 (1 empty cell)
        - Headers: "Planned for Month of SEPTEMBER 2025", "ACHIEVED FOR month SEPTEMBER 2025"
        - Searches: "NEST_AUGUST_2025"
        - Copies: N10:end → G10:end in DPR sheet
    """
    try:
        from datetime import datetime
        
        current_year = datetime.now().year
        
        # Create new spreadsheet name
        new_spreadsheet_name = f"{request.project_name.upper()}_{request.month.upper()}_{current_year}"
        
        # Step 1: Copy the source spreadsheet
        copy_result = await mcp_client.copy_spreadsheet(
            google_id=current_user['google_id'],
            source_spreadsheet_id=request.spreadsheet_id,
            new_name=new_spreadsheet_name
        )
        
        if not copy_result.get('success', False):
            return CopySpreadsheetResponse(
                success=False,
                new_spreadsheet_id="",
                spreadsheet_name=new_spreadsheet_name,
                data_copied=False,
                message="Failed to copy spreadsheet",
                error=copy_result.get('error', 'Unknown error')
            )
        
        new_spreadsheet_id = copy_result['new_spreadsheet_id']
        
        # Step 2: Populate monthly dates and headers in the new spreadsheet
        date_populate_result = await mcp_client.populate_monthly_dates(
            google_id=current_user['google_id'],
            spreadsheet_id=new_spreadsheet_id,
            sheet_name="DPR",  # Assuming DPR sheet
            month=request.month,
            year=current_year
        )
        
        date_populate_message = ""
        if date_populate_result.get('success', False):
            days_populated = date_populate_result.get('days_populated', 0)
            empty_cells = date_populate_result.get('empty_cells', 0)
            date_populate_message = f"Populated {days_populated} days, {empty_cells} empty cells. "
        else:
            date_populate_message = f"Date population failed: {date_populate_result.get('error', 'Unknown error')}. "
        
        # Step 3: Find previous month's spreadsheet
        try:
            previous_month, previous_year = mcp_client.get_previous_month_year(request.month, current_year)
            previous_spreadsheet_name = f"{request.project_name.upper()}_{previous_month}_{previous_year}"
            
            # Search for previous month's spreadsheet
            search_result = await mcp_client.search_spreadsheet_by_name(
                google_id=current_user['google_id'],
                spreadsheet_name=previous_spreadsheet_name
            )
            
            data_copied = False
            copy_message = "No previous month data to copy"
            
            if search_result.get('success', False) and search_result.get('found', False):
                # Step 3: Copy data from previous month's N10:end to new spreadsheet's G10:end
                previous_spreadsheet_id = search_result['spreadsheet_id']
                
                data_copy_result = await mcp_client.copy_column_data(
                    google_id=current_user['google_id'],
                    source_spreadsheet_id=previous_spreadsheet_id,
                    target_spreadsheet_id=new_spreadsheet_id,
                    source_sheet="DPR",
                    target_sheet="DPR",
                    source_column="N",
                    target_column="G",
                    start_row=10
                )
                
                if data_copy_result.get('success', False) and data_copy_result.get('data_copied', False):
                    data_copied = True
                    rows_copied = data_copy_result.get('rows_copied', 0)
                    copy_message = f"Copied {rows_copied} rows from {previous_spreadsheet_name} (N10:end → G10:end)"
                else:
                    copy_message = f"Found {previous_spreadsheet_name} but no data to copy or copy failed"
            else:
                copy_message = f"Previous month spreadsheet '{previous_spreadsheet_name}' not found"
                
        except ValueError as e:
            copy_message = f"Invalid month name: {request.month}"
            data_copied = False
        except Exception as e:
            copy_message = f"Error processing previous month data: {str(e)}"
            data_copied = False
        
        return CopySpreadsheetResponse(
            success=True,
            new_spreadsheet_id=new_spreadsheet_id,
            spreadsheet_name=new_spreadsheet_name,
            data_copied=data_copied,
            message=f"{date_populate_message}{copy_message}"
        )
        
    except Exception as e:
        return CopySpreadsheetResponse(
            success=False,
            new_spreadsheet_id="",
            spreadsheet_name="",
            data_copied=False,
            message="Failed to process request",
            error=f"Processing error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)