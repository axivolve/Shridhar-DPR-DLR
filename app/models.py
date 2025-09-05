from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    id: Optional[str] = None
    google_id: str
    email: str
    name: str
    access_token: str
    refresh_token: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class WriteResponse(BaseModel):
    success: bool
    message: str
    sheet_id: str
    range_written: str

class Document(BaseModel):
    id: str
    name: str
    mimeType: str
    createdTime: str
    modifiedTime: str
    webViewLink: str

class DocumentListResponse(BaseModel):
    documents: List[Document]
