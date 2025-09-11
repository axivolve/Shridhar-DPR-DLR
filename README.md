# AI Works Tracker System

A comprehensive FastAPI application for managing Daily Progress Reports (DPR) and Daily Log Reports (DLR) with Google Sheets integration, AI-powered analysis, and automated spreadsheet management.

## 🚀 Project Structure

```
Shridhar_DPR/
│
├── app/
│   ├── __init__.py
│   ├── main.py              # Main FastAPI app with all routes
│   ├── config.py            # Environment variables and configuration
│   ├── database.py          # Supabase connection and user management
│   ├── google_auth.py       # Google OAuth, Sheets, and Drive integration
│   ├── models.py            # Pydantic data models and response schemas
│   ├── mcp_client.py        # MCP integration and advanced Google Sheets operations
│   ├── llm_response.py      # LLM agent configuration and prompt building
│   └── fuzzy_matching.py    # Fuzzy string matching utilities
│
├── sql/
│   └── create_users_table.sql  # Database schema for user management
│
├── static/                   # Static web assets
├── tests/
│   └── __init__.py          # Test suite initialization
├── .env                     # Environment variables (create from .env.example)
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Project configuration
├── uv.lock                 # Dependency lock file
└── run.py                  # Application entry point
```

## 🎯 Key Features

### 🔐 Authentication & Security
- **Google OAuth2 Integration**: Secure authentication with Google accounts
- **JWT Token Management**: Session management with JSON Web Tokens
- **User Persistence**: User data and tokens stored in Supabase
- **Scope Management**: Granular Google API permissions

### 📊 Google Sheets Integration
- **Advanced Data Retrieval**: Read sheet data with actual row indices
- **Column-Specific Operations**: Extract entire columns from specific starting points
- **Row-Based Operations**: Get row data with column names as keys
- **Batch Cell Updates**: Multiple cell operations (add, remove, replace)
- **Comprehensive Logging**: All operations logged to dedicated LOG sheets

### 🤖 AI-Powered Analysis
- **LLM Integration**: Groq-powered AI analysis using Meta-Llama models
- **Natural Language Processing**: Convert user queries to structured operations
- **Date Intelligence**: Automatic date extraction and validation
- **Structured Responses**: Type-safe AI responses with Pydantic models

### 📅 Automated Spreadsheet Management
- **Monthly Sheet Creation**: Automated copying with proper naming conventions
- **Date Population**: Automatic date headers in DD-MM-YYYY format
- **Previous Month Data Transfer**: Smart data copying from previous periods
- **Dynamic Headers**: Auto-generated month/year headers
- **Intelligent Formatting**: Proper text formatting and orientation

### 📈 DPR/DLR Operations
- **Real-Time Updates**: Live cell updates based on natural language input
- **Activity Tracking**: Comprehensive logging of all modifications
- **Progress Monitoring**: Track daily progress with structured data
- **Multi-Project Support**: Handle multiple projects with proper isolation

## 🛠️ API Endpoints

### Authentication Endpoints
- `GET /` - Homepage with Google Sign-In interface
- `GET /auth/login` - Initiate Google OAuth2 authentication flow
- `GET /auth/callback` - Handle Google OAuth2 callback and token exchange
- `GET /user/me` - Get current authenticated user information

### Documentation Endpoints
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)
- `GET /openapi.json` - OpenAPI specification

### Google Sheets Basic Operations
- `GET /documents` - List all accessible Google Sheets for the user

### MCP-Powered Data Retrieval
- `GET /mcp/sheet-data/{sheet_id}` - Get sheet data with 0-based indexing
- `GET /mcp/column-data/{sheet_id}` - Extract entire column data from starting cell
- `GET /mcp/row-data/{sheet_id}` - Get row data with column names as keys

### AI-Powered Sheet Management
- `POST /update-dpr/{sheet_id}` - AI-powered DPR update processor
  - Natural language query processing
  - Automatic cell calculations and updates
  - Comprehensive operation logging
  - Date extraction and validation

- `POST /update-dlr/{sheet_id}` - AI-powered DLR update processor with fuzzy matching
  - Fuzzy string matching for worker categories and locations
  - Direct cell updates using column + row pattern
  - Real-time cell value additions
  - Comprehensive operation logging

- `POST /analyze-logs/{sheet_id}` - AI-powered log analysis and insights
  - Natural language queries on operation logs
  - Pattern recognition and trend analysis
  - Analytics and reporting capabilities
  - Historical data insights

### Spreadsheet Management
- `POST /new-spreadsheet` - Create monthly spreadsheet copies
  - Automated naming: `{PROJECT}_{MONTH}_{YEAR}`
  - Date population in specified ranges
  - Previous month data transfer
  - Dynamic header generation

## 📋 Detailed Endpoint Documentation

## 🎯 Main POST Endpoints

### 1. `/update-dpr/{sheet_id}` (POST)
**Purpose**: AI-powered Daily Progress Report updates with natural language processing.

**Request Body**:
```json
{
  "site_engineer_name": "John Doe",
  "phone_number": "1234567890",
  "users_query": "Villa 101 excavation completed 50 cubic meters on 15 September 2025"
}
```

**Process Flow**:
1. Extract element data from column B (starting row 10) from DPR sheet
2. Extract activity data from range C10:E96 from DPR sheet
3. Build AI prompt with user query and sheet data
4. Process through LLM for structured analysis with date extraction
5. Find target column by matching operation date with row 8AV:8BZ
6. Calculate target cells using element_index + activity_index
7. Perform batch cell updates (add/remove/replace operations)
8. Log all operations to LOG sheet with DPR identifier

**Response**:
```json
{
  "success": true,
  "site_engineer_name": "John Doe",
  "phone_number": "1234567890",
  "sheet_id": "1ABC123...",
  "sheet_name": "DPR",
  "users_query": "Villa 101 excavation completed 50 cubic meters on 15 September 2025",
  "element_data_summary": "Column B data from row 10: 12 rows retrieved",
  "activity_data_summary": "Range C10:E96 data (0-indexed): 87 rows retrieved. Updated 2/2 cells successfully",
  "llm_result": {
    "element_index": ["10", "15"],
    "activity_index": ["1", "2"],
    "activity_quantities": [["50", "add"], ["25", "replace"]],
    "agent_feedback": ["Villa 101 excavation completed with 50 cubic meters on 15 September 2025"],
    "operation_date": "15-09-2025"
  },
  "error": null
}
```

**Key Features**:
- **Date Intelligence**: Supports "15 September 2025", "15/09/2025", "today", "yesterday"
- **Future Date Correction**: Automatically corrects future dates to today
- **Multiple Operations**: Handles multiple villas/activities in single query
- **Cell Calculation**: Target cell = element_index + activity_index (e.g., 10+1=11 → BC11)

---

### 2. `/update-dlr/{sheet_id}` (POST)
**Purpose**: AI-powered Daily Log Report updates with fuzzy matching for worker categories.

**Request Body**:
```json
{
  "site_engineer_name": "Jane Smith",
  "phone_number": "0987654321",
  "users_query": "Grinder work for Villa 101 completed with 100 labors"
}
```

**Process Flow**:
1. Extract column data from 8A in DLR sheet (worker categories) with real indexing
2. Extract row data from range 6A:6ZZ in DLR sheet (villa/location data)
3. Run fuzzy matching on both datasets using user query (10 matches each)
4. Build AI prompt with fuzzy matching results and user query
5. Process through specialized DLR LLM agent
6. Perform direct cell updates using columns_index[i] + row_index[i] pattern
7. Log all operations to LOG sheet with DLR identifier

**Response**:
```json
{
  "success": true,
  "site_engineer_name": "Jane Smith",
  "phone_number": "0987654321",
  "sheet_id": "1ABC123...",
  "users_query": "Grinder work for Villa 101 completed with 100 labors",
  "column_data_summary": "Column data from 8A (real indexing): 25 rows retrieved. Fuzzy matches: 3",
  "row_data_summary": "Row data from 6A:6ZZ: 52 columns retrieved. Fuzzy matches: 2. Updated 1/1 cells successfully",
  "llm_result": {
    "row_index": ["14"],
    "columns_index": ["D"],
    "quantities": [100.0],
    "feedbacks": ["Grinder work for Villa 101 completed with 100 labors"]
  },
  "error": null
}
```

**Key Features**:
- **Fuzzy Matching**: Intelligent matching for worker types (Grinder, Mason, Carpenter, etc.)
- **Direct Cell Updates**: Updates cell D14 directly (column D + row 14)
- **Add Operations**: Always adds values to existing cell content
- **Auto-Correction**: Handles swapped row/column formats from LLM
- **No Date Processing**: DLR updates don't require date extraction

---

### 3. `/analyze-logs/{sheet_id}` (POST)
**Purpose**: AI-powered analysis of operation logs with natural language queries.

**Request Body**:
```json
{
  "users_query": "Show me all updates by John Doe last week and provide analytics"
}
```

**Process Flow**:
1. Retrieve all log data from LOG sheet (up to 1000 entries)
2. Filter and format data as list of lists (no headers)
3. Build analysis prompt with log data and user query
4. Process through specialized logs LLM agent
5. Return comprehensive analysis and insights

**Response**:
```json
{
  "success": true,
  "sheet_id": "1ABC123...",
  "logs_processed": 156,
  "query": "Show me all updates by John Doe last week and provide analytics",
  "feedback": "**John Doe's Activity Summary (Last Week)**\n\n| Date | Updates | DPR | DLR | Total Value |\n|------|---------|-----|-----|-------------|\n| 09-09 | 5 | 3 | 2 | 250 units |\n| 08-09 | 3 | 2 | 1 | 150 units |\n\n**Key Insights:**\n- Most active on 09-09-2025 with 5 updates\n- Primary focus on Villa 101 and Villa 102\n- Average update value: 50 units\n- DPR:DLR ratio is 3:2",
  "error": null
}
```

**Log Data Format** (each row as list):
```
[timestamp, site_engineer, phone, row, column, value, type, operation_date, user_query, feedback, sheet_name]
```

**Example Queries**:
- `"Show me all updates by John Doe last week"`
- `"What are the most common operations?"`
- `"Give me analytics on DPR vs DLR updates"`
- `"Show updates for Villa 101 with trends"`
- `"Compare performance between engineers"`

**Key Features**:
- **Natural Language Queries**: Ask questions in plain English
- **Comprehensive Analysis**: Patterns, trends, and insights
- **Tabular Responses**: Formatted tables for analytics requests
- **Historical Data**: Access to complete operation history
- **Multi-Sheet Analysis**: Combines DPR and DLR operations

---

### 4. `/new-spreadsheet` (POST)
**Purpose**: Create monthly project spreadsheets with automated setup and data transfer.

**Request Body**:
```json
{
  "spreadsheet_id": "1XYZ789_source_sheet_id",
  "project_name": "NEST",
  "month": "SEPTEMBER"
}
```

**Process Flow**:
1. Create copy of source spreadsheet using Google Drive API
2. Rename with format: `{PROJECT_NAME}_{MONTH}_{CURRENT_YEAR}`
3. Populate monthly dates in P8:AT8 and AV8:BZ8 ranges
4. Update merged cell headers with month/year information
5. Search for previous month's spreadsheet in user's Drive
6. Copy data from previous month's N10:end to new sheet's G10:end
7. Return comprehensive status with all operations

**Response**:
```json
{
  "success": true,
  "new_spreadsheet_id": "1NEW123_generated_id",
  "spreadsheet_name": "NEST_SEPTEMBER_2025",
  "data_copied": true,
  "message": "Populated 30 days, 1 empty cells. Copied 25 rows from NEST_AUGUST_2025 (N10:end → G10:end)",
  "error": null
}
```

**Date Population Rules**:
- **31-day months**: Jan, Mar, May, Jul, Aug, Oct, Dec → Fill all 31 cells
- **30-day months**: Apr, Jun, Sep, Nov → Fill 30 cells, leave 1 empty
- **February**: Always 29 days → Fill 29 cells, leave 2 empty

**Header Updates**:
- **P7:AT7**: `"Planned for Month of SEPTEMBER 2025"`
- **AV7:BZ7**: `"ACHIEVED FOR month SEPTEMBER 2025"`

**Data Transfer Logic**:
- **Search Pattern**: `{PROJECT_NAME}_{PREVIOUS_MONTH}_{YEAR}`
- **Year Transitions**: January 2025 → looks for December 2024
- **Copy Operation**: N10:end (source) → G10:end (target) in DPR sheet
- **Fallback**: Proceeds without data copy if previous month not found

**Key Features**:
- **Intelligent Naming**: Automatic year calculation and formatting
- **Smart Date Population**: Month-specific day counts with proper formatting
- **Previous Month Detection**: Automatic search and data transfer
- **Year Boundary Handling**: Correct transitions across year boundaries
- **Comprehensive Logging**: Detailed status of all operations

## 🔧 Configuration

### Environment Variables (.env)
```env
# Google OAuth2
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/callback

# Supabase Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret
JWT_ALGORITHM=HS256

# AI/LLM Integration
GROQ_API_KEY=your_groq_api_key
```

### Google API Scopes
```python
GOOGLE_SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'  # Required for spreadsheet copying
]
```

## 🚀 Setup Instructions

### 1. Prerequisites
- Python 3.8+
- Google Cloud Project with Sheets and Drive APIs enabled
- Supabase account and database
- Groq API access

### 2. Installation
```bash
# Clone the repository
git clone <repository_url>
cd Shridhar_DPR

# Install dependencies using uv (recommended)
uv sync
# OR using pip
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your credentials
```

### 3. Database Setup
```bash
# Execute the SQL schema in your Supabase dashboard
cat sql/create_users_table.sql
```

### 4. Google Cloud Setup
1. Create a Google Cloud Project
2. Enable Google Sheets API and Google Drive API
3. Create OAuth2 credentials (Web application)
4. Add `http://localhost:8000/callback` to authorized redirect URIs
5. Add your credentials to `.env`

### 5. Run the Application
```bash
# Development server
python run.py
# OR
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 6. Access the Application
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 🧪 Testing

### Manual Testing Flow
1. Visit http://localhost:8000
2. Click "Sign in with Google"
3. Complete OAuth flow
4. Copy JWT token from response
5. Use token in API requests (Authorization: Bearer <token>)

### Example API Calls
```bash
# List accessible sheets
curl -H "Authorization: Bearer <token>" \
     http://localhost:8000/documents

# Create monthly spreadsheet
curl -X POST \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"spreadsheet_id":"abc123","project_name":"NEST","month":"SEPTEMBER"}' \
     http://localhost:8000/new-spreadsheet

# Process DPR update
curl -X POST \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"site_engineer_name":"John Doe","phone_number":"1234567890","users_query":"Villa 101 excavation 50 cubic meters on 15 September 2025"}' \
     http://localhost:8000/update-dpr/abc123

# Process DLR update
curl -X POST \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"site_engineer_name":"Jane Smith","phone_number":"0987654321","users_query":"Grinder work for Villa 101 completed with 100 labors"}' \
     http://localhost:8000/update-dlr/abc123

# Analyze logs
curl -X POST \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"users_query":"Show me all updates by John Doe last week"}' \
     http://localhost:8000/analyze-logs/abc123
```

## 📊 Data Models

### DPR Update Models
```python
class UpdatedSheetRequest(BaseModel):
    site_engineer_name: str
    phone_number: str
    users_query: str

class DPRUpdationResult(BaseModel):
    element_index: List[str]  # Element indices from user query
    activity_index: List[str]  # Activity indices from user query  
    activity_quantities: List[Tuple[str, str]]  # [(quantity, operation_type)]
    agent_feedback: List[str]  # AI feedback messages
    operation_date: str  # Extracted date in DD-MM-YYYY format

class UpdatedSheetResponse(BaseModel):
    success: bool
    site_engineer_name: str
    phone_number: str
    sheet_id: str
    sheet_name: str  # Always "DPR"
    users_query: str
    element_data_summary: str
    activity_data_summary: str
    llm_result: Optional[DPRUpdationResult]
    error: Optional[str]
```

### DLR Update Models
```python
class UpdatedDLRRequest(BaseModel):
    site_engineer_name: str
    phone_number: str
    users_query: str

class DLRUpdationResult(BaseModel):
    row_index: List[str]  # Row indices from user query
    columns_index: List[str]  # Column indices from user query
    quantities: List[float]  # Quantities to update
    feedbacks: List[str]  # AI feedback messages

class UpdatedDLRResponse(BaseModel):
    success: bool
    site_engineer_name: str
    phone_number: str
    sheet_id: str
    users_query: str
    column_data_summary: str
    row_data_summary: str
    llm_result: Optional[DLRUpdationResult]
    error: Optional[str]
```

### Log Analysis Models
```python
class AnalyzeLogsRequest(BaseModel):
    users_query: str

class AnalyzeLogsResponse(BaseModel):
    success: bool
    sheet_id: str
    logs_processed: int
    query: str
    feedback: str  # AI analysis result
    error: Optional[str]

class LogQueryResult(BaseModel):
    result: str  # LLM analysis result
```

### Spreadsheet Management Models
```python
class CopySpreadsheetRequest(BaseModel):
    spreadsheet_id: str  # Source spreadsheet ID
    project_name: str    # e.g., "NEST"
    month: str          # e.g., "SEPTEMBER"

class CopySpreadsheetResponse(BaseModel):
    success: bool
    new_spreadsheet_id: str
    spreadsheet_name: str  # e.g., "NEST_SEPTEMBER_2025"
    data_copied: bool
    message: str  # Detailed operation status
    error: Optional[str]
```

### Sheet Data Response Models
```python
class SheetDataResponse(BaseModel):
    success: bool
    spreadsheet_id: str
    sheet: str
    range: str
    data: Dict[int, List[str]]  # {row_number: [cell_values]}
    row_count: int
    column_count: int
    total_rows_processed: Optional[int]
    start_row: Optional[int]
    error: Optional[str]

class ColumnDataResponse(BaseModel):
    success: bool
    spreadsheet_id: str
    sheet: str
    cell_reference: str  # e.g., "C3"
    column: str  # e.g., "C"
    start_row: int  # e.g., 3
    data: Dict[int, List[str]]  # {row_number: [value]}
    row_count: int
    total_rows_processed: int
    stopped_due_to_empty_rows: bool
    error: Optional[str]

class RowDataResponse(BaseModel):
    success: bool
    spreadsheet_id: str
    sheet: str
    range: str
    row: int
    data: Dict[str, str]  # {column_name: value}
    column_count: int
    error: Optional[str]
```

## 🔍 Advanced Features

### Date Intelligence
- **Format Support**: "January 15, 2024", "15/01/2024", "today", "yesterday"
- **Validation**: Future date correction, multiple date detection
- **Localization**: DD-MM-YYYY format for all outputs

### Fuzzy Matching System
- **Intelligent String Matching**: Uses `rapidfuzz` for similarity-based matching
- **Worker Category Recognition**: Matches "Grinder" with "Grinder work", "Mason" with "Masonry"
- **Location Matching**: Identifies "Villa 101" from "Villa101", "Building A" variations
- **Top Results**: Returns 5 best matches with original keys and values
- **Multi-Format Support**: Handles both `Dict[str, str]` and `Dict[str, List[str]]` inputs

### Logging System
- **Comprehensive Tracking**: Every operation logged with full context
- **Structured Data**: Timestamp, engineer, phone, row, column, value, type, operation date, user query, feedback, sheet name
- **Sheet Identification**: Distinguishes between DPR and DLR operations
- **Audit Trail**: Complete history of all modifications with searchable logs
- **AI Analysis Ready**: Log data formatted for natural language queries and analytics

### Error Handling
- **Graceful Degradation**: Operations continue even if sub-components fail
- **Detailed Messages**: Clear error descriptions for debugging
- **Fallback Mechanisms**: Alternative approaches when primary methods fail

### Performance Optimizations
- **Batch Operations**: Multiple cell updates in single API calls
- **Efficient Queries**: Optimized data retrieval patterns
- **Caching**: Smart token and metadata caching

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
1. Check the API documentation at `/docs`
2. Review the error logs for detailed messages
3. Ensure all environment variables are properly configured
4. Verify Google API quotas and permissions

## 🔮 Future Enhancements

- **Multi-language Support**: Internationalization for global usage
- **Advanced Analytics**: Dashboard with progress visualization  
- **Mobile App**: React Native companion application
- **Webhook Integration**: Real-time notifications and updates
- **Template System**: Customizable sheet templates for different projects
- **Bulk Operations**: Handle multiple projects simultaneously