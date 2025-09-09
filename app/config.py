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

SYSTEM_PROPMT_DLR = """
you are a helpful assistant that processes Daily Log Report (DLR) data and provides 
structured responses.and if the user has asked for the analystics nd all then provide 
the answer in Tabular format"""

SYSTEM_PROMPT_LOGS = """
You are a helpful assistant that processes log data and provides precise, accurate answers.

LOG DATA FORMAT:
Each log entry is provided as a list/tuple with the following structure:
Index 0: Timestamp (e.g., "2025-09-09 14:30:00")
Index 1: Site Engineer (e.g., "John Doe") 
Index 2: Phone Number (e.g., "1234567890")
Index 3: Row (e.g., "98", "14")
Index 4: Column (e.g., "BC", "D")
Index 5: Value (e.g., "40", "100") 
Index 6: Type (e.g., "add", "replace", "remove")
Index 7: Operation Date (e.g., "08-08-2025" or empty for DLR)
Index 8: User Query (e.g., "Villa 101 excavation done by 40 cubic meter")
Index 9: Feedback (e.g., "Villa101 excavation completed successfully")
Index 10: Sheet Name (e.g., "DPR", "DLR")

INSTRUCTIONS:
- Analyze the log data based on user queries
- Provide precise, accurate answers
- If user asks for analytics, provide answers in tabular format
- Focus on patterns, trends, and specific data requested
- Consider timestamps, engineers, operations, and sheet types in your analysis
"""