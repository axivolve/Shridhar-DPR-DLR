# Shridhar DPR-DLR Management System

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
│   └── llm_response.py      # LLM agent configuration and prompt building
│
├── mcp/
│   ├── connect_sheet.py     # MCP server connection utilities
│   ├── test_email.py        # Email testing utilities
│   └── tool_call.py         # MCP tool call implementations
│
├── sql/
│   └── create_users_table.sql  # Database schema for user management
│
├── static/                   # Static web assets
├── tests/                    # Test suite
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
- `GET /login` - Initiate Google OAuth2 authentication flow
- `GET /callback` - Handle Google OAuth2 callback and token exchange
- `GET /me` - Get current authenticated user information

### Google Sheets Basic Operations
- `GET /documents` - List all accessible Google Sheets for the user
- `POST /write-hello-world/{sheet_id}` - Write test data to a specific sheet

### MCP-Powered Advanced Operations
- `GET /mcp/sheet-data/{sheet_id}` - Get sheet data with 0-based indexing
- `GET /mcp/column-data/{sheet_id}` - Extract entire column data from starting cell
- `GET /mcp/row-data/{sheet_id}` - Get row data with column names as keys

### AI-Powered DPR Management
- `POST /update_dpr/{sheet_id}` - AI-powered DPR update processor
  - Natural language query processing
  - Automatic cell calculations and updates
  - Comprehensive operation logging
  - Date extraction and validation

### Spreadsheet Management
- `POST /new-spreadsheet` - Create monthly spreadsheet copies
  - Automated naming: `{PROJECT}_{MONTH}_{YEAR}`
  - Date population in specified ranges
  - Previous month data transfer
  - Dynamic header generation

## 📋 Detailed Endpoint Documentation

### `/update_dpr/{sheet_id}` (POST)
**Purpose**: Process natural language queries to update DPR sheets with AI assistance.

**Request Body**:
```json
{
  "site_engineer_name": "John Doe",
  "phone_number": "1234567890",
  "sheet_name": "DPR",
  "users_query": "Villa 101 excavation completed 50 cubic meters on 15 September 2025"
}
```

**Process Flow**:
1. Extract element data from column B (starting row 10)
2. Extract activity data from range C10:E96
3. Build AI prompt with user query and sheet data
4. Process through LLM for structured analysis
5. Extract operation date with intelligent parsing
6. Calculate target cells and perform updates
7. Log all operations to LOG sheet

**Response**:
```json
{
  "success": true,
  "site_engineer_name": "John Doe",
  "phone_number": "1234567890",
  "sheet_id": "abc123...",
  "sheet_name": "DPR",
  "users_query": "Villa 101 excavation...",
  "element_data_summary": "Column B data from row 10: 12 rows retrieved",
  "activity_data_summary": "Range C10:E96 data (0-indexed): 87 rows retrieved. Updated 2/2 cells successfully",
  "llm_result": {
    "element_index": ["10", "15"],
    "activity_index": ["1", "2"],
    "activity_quantities": [["50", "add"], ["25", "replace"]],
    "agent_feedback": ["Operations completed successfully"],
    "operation_date": "15-09-2025"
  }
}
```

### `/new-spreadsheet` (POST)
**Purpose**: Create monthly project spreadsheets with automated setup.

**Request Body**:
```json
{
  "spreadsheet_id": "source_sheet_id",
  "project_name": "NEST",
  "month": "SEPTEMBER"
}
```

**Features**:
- **Naming Convention**: Creates `NEST_SEPTEMBER_2025`
- **Date Population**: 
  - P8:AT8 range with dates 01-09-2025 to 30-09-2025
  - AV8:BZ8 range with duplicate dates
  - Handles month-specific day counts (Feb=29, Apr/Jun/Sep/Nov=30, others=31)
- **Header Updates**:
  - P7:AT7: "Planned for Month of SEPTEMBER 2025"
  - AV7:BZ7: "ACHIEVED FOR month SEPTEMBER 2025"
- **Data Transfer**: Copies N10:end → G10:end from previous month's sheet
- **Year Transitions**: Handles January→December transitions correctly

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

# Install dependencies
pip install -r requirements.txt
# OR using uv (recommended)
uv install

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
     -d '{"site_engineer_name":"John","phone_number":"123","sheet_name":"DPR","users_query":"Villa 101 excavation 50 cubic meters"}' \
     http://localhost:8000/update_dpr/abc123
```

## 📊 Data Models

### DPR Update Result
```python
class DPRUpdationResult(BaseModel):
    element_index: List[str]  # Element indices from user query
    activity_index: List[str]  # Activity indices from user query  
    activity_quantities: List[Tuple[str, str]]  # [(quantity, operation_type)]
    agent_feedback: List[str]  # AI feedback messages
    operation_date: str  # Extracted date in DD-MM-YYYY format
```

### Sheet Data Response
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
```

## 🔍 Advanced Features

### Date Intelligence
- **Format Support**: "January 15, 2024", "15/01/2024", "today", "yesterday"
- **Validation**: Future date correction, multiple date detection
- **Localization**: DD-MM-YYYY format for all outputs

### Logging System
- **Comprehensive Tracking**: Every operation logged with full context
- **Structured Data**: Timestamp, engineer, operation details, user query
- **Audit Trail**: Complete history of all modifications

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