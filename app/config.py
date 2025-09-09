import os
from dotenv import load_dotenv

load_dotenv()

# Google OAuth2 Settings
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

# Google API Scopes
GOOGLE_SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'  # Full Drive access for copying files
]

# Supabase Settings
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# JWT Settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24

# App Settings
APP_URL = os.getenv("APP_URL")

# Groq API Settings
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SYSTEM_PROMPT_DPR = """
according to the given data please provide the below things which is mentioned"""


SYSTEM_PROPMT_DLR = """ """