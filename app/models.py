from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict, Tuple
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

class SheetDataResponse(BaseModel):
    success: bool
    spreadsheet_id: str
    sheet: str
    range: str
    data: Dict[int, List[str]]  # Changed to Dict with row numbers as keys
    row_count: int
    column_count: int
    total_rows_processed: Optional[int] = None  # Total rows from Google Sheets (including empty)
    start_row: Optional[int] = None  # Starting row number from the range
    error: Optional[str] = None

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
    error: Optional[str] = None

class MCPToolResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

class DPRUpdationResult(BaseModel):
    element_index: List[str] = Field(description="list of the element index mentioned in the user's query")
    activity_index: List[str] = Field(description="list of the activity index mentioned in the user's query")
    activity_quantities: List[Tuple[str, str]] = Field(description="list of tuple of the activity quantities with the type (like add updation or replace updation or remove updation)")
    agent_feedback: List[str] = Field(description="list of the agent feedback for the user's query just an single feedback for whole query")
    operation_date: str = Field(description="Date when the operation occurred in DD-MM-YYYY format. Extract from user query or use today's date. If multiple dates mentioned, leave empty and provide error feedback.")

class DLRUpdationResult(BaseModel):
    row_index: List[str] = Field(description="list of the row index mentioned in the user's query")
    columns_index: List[str] = Field(description="list of the column index mentioned in the user's query")
    activity_quantities: List[Tuple[str, str]] = Field(description="list of tuple of the activity quantities with the type (like add updation or replace updation or remove updation)")
    feedbacks: List[str] = Field(description="list of the agent feedback for the user's query just an single feedback for whole query")

class LogQueryResult(BaseModel):
    result: str = Field(description="Answer of the given Query based on the provide logs data")

class UpdatedSheetRequest(BaseModel):
    site_engineer_name: str
    phone_number: str
    users_query: str

class UpdatedSheetResponse(BaseModel):
    success: bool
    site_engineer_name: str
    phone_number: str
    sheet_id: str
    sheet_name: str
    users_query: str
    element_data_summary: str  # Summary of B10 column data
    activity_data_summary: str  # Summary of C10:E96 range data
    llm_result: Optional[DPRUpdationResult] = None
    error: Optional[str] = None

class RowDataResponse(BaseModel):
    success: bool
    spreadsheet_id: str
    sheet: str
    range: str
    row: int
    data: Dict[str, str]  # {column_name: value} e.g., {"A": "data1", "B": "data2"}
    column_count: int
    error: Optional[str] = None

class CopySpreadsheetRequest(BaseModel):
    spreadsheet_id: str
    project_name: str
    month: str

class CopySpreadsheetResponse(BaseModel):
    success: bool
    new_spreadsheet_id: str
    spreadsheet_name: str
    data_copied: bool
    message: str
    error: Optional[str] = None

class DLRUpdationResult(BaseModel):
    row_index: List[str] = Field(description="list of the row index mentioned in the user's query")
    columns_index: List[str] = Field(description="list of the column index mentioned in the user's query")
    quantities: List[float] = Field(description="list of the quantities mentioned in the user's query")
    feedbacks: List[str] = Field(description="list of the agent feedback for the user's query just a single feedback for whole query")

class UpdatedDLRRequest(BaseModel):
    site_engineer_name: str
    phone_number: str
    users_query: str

class UpdatedDLRResponse(BaseModel):
    success: bool
    site_engineer_name: str
    phone_number: str
    sheet_id: str
    users_query: str
    column_data_summary: str
    row_data_summary: str
    llm_result: Optional[DLRUpdationResult] = None
    error: Optional[str] = None