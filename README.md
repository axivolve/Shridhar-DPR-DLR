## Shridhar-DPR-DLR

# Simple FastAPI Google Sheets Connection

```
fastapi-google-sheets/
│
├── app/
│   ├── __init__.py
│   ├── main.py              # Main FastAPI app with all routes
│   ├── config.py            # Environment variables and configuration
│   ├── database.py          # Supabase connection and user management
│   ├── google_auth.py       # Google OAuth, Sheets, and Drive integration
│   └── models.py            # Data models and response schemas
│
├── sql/
│   └── create_users_table.sql  # SQL for setting up the users table
│
├── static/                   # Static files (CSS, JS, etc.)
│   └── index.html           # Test page with "Sign in with Google" button
│
├── .env                     # Your environment variables
├── .env.example            # Example environment file
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## **What each file does:**

- **`main.py`**: FastAPI application with these endpoints:
  - `GET /`: Homepage with Google Sign-In
  - `GET /login`: Initiate Google OAuth2 flow
  - `GET /callback`: Handle Google OAuth2 callback
  - `POST /write-hello-world/{sheet_id}`: Write to a Google Sheet
  - `GET /documents`: List all accessible Google Sheets
  - `GET /me`: Get current user info

- **`config.py`**: Configuration including:
  - Google OAuth2 credentials
  - JWT settings
  - Supabase connection details
  - Google API scopes

- **`database.py`**: Manages user data and tokens in Supabase
- **`google_auth.py`**: Handles:
  - Google OAuth2 authentication
  - JWT token management
  - Google Sheets and Drive API interactions
- **`models.py`**: Pydantic models for:
  - User data
  - API responses
  - Document metadata

## **The flow:**
1. Visit `http://localhost:8000` → Click "Sign in with Google"
2. After login → Get JWT token
3. Available endpoints:
   - `GET /documents`: List all accessible Google Sheets
   - `POST /write-hello-world/{sheet_id}`: Write to a specific sheet
   - `GET /me`: Get current user information

## **Features:**
- Secure Google OAuth2 authentication
- List all accessible Google Sheets
- Write to Google Sheets
- Token-based authentication with JWT
- User session management with Supabase

## **Setup:**
1. Copy `.env.example` to `.env` and fill in your credentials
2. Run `pip install -r requirements.txt`
3. Start the server: `uvicorn run:app --reload`
4. Visit `http://localhost:8000` to test

## **API Documentation:**
Once running, visit `http://localhost:8000/docs` for interactive API documentation with Swagger UI.