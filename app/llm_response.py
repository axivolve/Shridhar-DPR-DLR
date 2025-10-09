from agno.agent import Agent
from agno.models.groq import Groq
from pydantic import BaseModel, Field
from dotenv import load_dotenv 
from app.config import SYSTEM_PROMPT_DPR, SYSTEM_PROMPT_LOGS, SYSTEM_PROMPT_DLR
from app.models import DPRUpdationResult, DLRUpdationResult, LogQueryResult

def get_support_agent(api_key: str) -> Agent:
    return Agent(
        model=Groq(id="meta-llama/llama-4-scout-17b-16e-instruct", api_key=api_key),
        system_message=SYSTEM_PROMPT_DPR,
        markdown=False,
        response_model=DPRUpdationResult,
        retries=10,
        add_datetime_to_instructions=True,
    )

def get_dlr_support_agent(api_key: str) -> Agent:
    """
    Agent specifically configured for DLR updates.
    Returns DLRUpdationResult instead of DPRUpdationResult.
    """
    return Agent(
        model=Groq(id="meta-llama/llama-4-scout-17b-16e-instruct", api_key=api_key),
        system_message=SYSTEM_PROMPT_DLR, 
        markdown=False,
        response_model=DLRUpdationResult,
        retries=10,
        add_datetime_to_instructions=True,
    )

def get_logs_support_agent(api_key: str) -> Agent:
    return Agent(
        model=Groq(id="meta-llama/llama-4-scout-17b-16e-instruct", api_key=api_key),
        system_message=SYSTEM_PROMPT_LOGS,
        markdown=True,
        response_model=LogQueryResult,
        retries=10,
        add_datetime_to_instructions=True 
)

def prompt_builder(element_data: str, activity_data: str, users_query: str) -> str:
    from datetime import datetime
    today_date = datetime.now().strftime("%d-%m-%Y")
    
    return f"""
here is the data of the sheet which is associated with it's indexing
    {element_data}
    {activity_data}
    
aand here is the user's query
user's query: {users_query}

now based on the user's query and the data of the sheet 
please provide the below things which is mentioned

element_index: list[str]
activity_index: list[str]
activity_quantities: list[tuple(str, str)]
agent_feedback: list[str]
operation_date: str

where the element index list is the number of element index mentioned in the user's query
where the activity index list is the number of activity index mentioned in the user's query
where the activity quantities list is the number of activity quantities mentioned in the user's query
where the agent feedback list is the feedback of the agent for the user's query keep it the single feedback every time for whole query
where the operation_date is the date extracted from user query in DD-MM-YYYY format

DATE EXTRACTION RULES:
1. If user mentions a specific date, extract it and convert to DD-MM-YYYY format
2. Supported date formats in user query: "January 15, 2024", "15/01/2024", "15-01-2024", "today", "yesterday"
3. If no date mentioned, use today's date: {today_date}
4. If multiple dates are mentioned, set operation_date to empty string "" and provide error feedback
5. Do not accept future dates - if future date detected, use today's date and mention in feedback
6. Do not accept complex relative dates like "last week", "2 days ago" - treat as no date mentioned

make sure the length of the every list should be same.. like 
number of element present in the element_index, activity_index, activity_quantities should be same just keep the single feedback 

DATE EXAMPLES:
"for Villah 101 Excavation has been done by 40 cubic meter on 15th January 2024"
element_index: ["10"] 
activity_index: ["1"]
activity_quantities: [["40", "add"]]
agent_feedback: ["for villah 101 excavation has been done by 40 cubic meter on 15th January 2024"]
operation_date: "15-01-2024"

"for Villah 101 Excavation has been done by 40 cubic meter today"
element_index: ["10"] 
activity_index: ["1"]
activity_quantities: [["40", "add"]]
agent_feedback: ["for villah 101 excavation has been done by 40 cubic meter today"]
operation_date: "{today_date}"

"for Villah 101 Excavation was done on 10/01/2024 and PCC on 15/01/2024"
element_index: []
activity_index: []
activity_quantities: []
agent_feedback: ["Multiple dates mentioned (10/01/2024 and 15/01/2024). Please specify single date for updation."]
operation_date: ""

OPERATION TYPES - Use appropriate operation based on user intent:
- "add": Adding/incrementing to existing quantity (most common)
- "replace": Setting exact quantity or correcting previous entries
- "remove": Clearing/resetting quantity to zero

REGULAR EXAMPLES:

ADD Operation Examples:
for Villah 101 Excavation has been done by 40 cubic meter and PCC has been done by 60 cubic meter
element_index: ["10", "10"] 
activity_index: ["1", "5"]
activity_quantities: [["40", "add"], ["60", "add"]]
agent_feedback: ["for villah 101 excavation and pcc has been done by 40 and 60 cubic meter"]
operation_date: "{today_date}"
     
for Villah 101 PCC has been done by 60 cubic meter
element_index: ["10"] 
activity_index: ["5"]
activity_quantities: [["60", "add"]]
agent_feedback: ["for villah 101 pcc has been done by 60 cubic meter"]
operation_date: "{today_date}"

for villah 101 and 102 has been done by 40 cubic meter
element_index: ["10", "97"] 
activity_index: ["1", "1"]
activity_quantities: [["40", "add"], ["40", "add"]]
agent_feedback: ["for villah 101 and 102 has been done by 40 cubic meter"]
operation_date: "{today_date}"

REPLACE Operation Examples:
Update Villah 101 Excavation quantity to exactly 100 cubic meter
element_index: ["10"] 
activity_index: ["1"]
activity_quantities: [["100", "replace"]]
agent_feedback: ["villah 101 excavation quantity set to exactly 100 cubic meter"]
operation_date: "{today_date}"

Set Villah 101 PCC to 80 cubic meter and Villah 102 Excavation to exactly 50 cubic meter
element_index: ["10", "97"] 
activity_index: ["5", "1"]
activity_quantities: [["80", "replace"], ["50", "replace"]]
agent_feedback: ["villah 101 pcc set to 80 and villah 102 excavation set to exactly 50 cubic meter"]
operation_date: "{today_date}"

REMOVE Operation Examples:
Clear all Excavation work for Villah 101
element_index: ["10"] 
activity_index: ["1"]
activity_quantities: [["0", "remove"]]
agent_feedback: ["villah 101 excavation work reset"]
operation_date: "{today_date}"

Reset PCC and Excavation for Villah 101
element_index: ["10", "10"] 
activity_index: ["5", "1"]
activity_quantities: [["0", "remove"], ["0", "remove"]]
agent_feedback: ["villah 101 pcc and excavation work reset"]
operation_date: "{today_date}"

MIXED Operation Examples:
Add 30 Excavation to Villah 101, set Villah 102 PCC to exactly 45, and clear Villah 103 Steel work
element_index: ["10", "97", "104"] 
activity_index: ["1", "5", "3"]
activity_quantities: [["30", "add"], ["45", "replace"], ["0", "remove"]]
agent_feedback: ["villah 101 excavation added 30, villah 102 pcc set to 45, villah 103 steel work reset"]
operation_date: "{today_date}"

these are the examples which i'm getting the output of the llm so you should give the output in the same manner
"""
    

def prompt_builder_for_dlr_updation(column_name: str, row_data: str, users_query: str) -> str:
    return f"""
    here is the data of the sheet which is associated with it's indexing
    here is the WORKER CATEGORIES with their ROW NUMBERS: {column_name}
    here is the VILLA/LOCATION DATA with their COLUMN LETTERS: {row_data}
    
    aand here is the user's query
    user's query: {users_query}
    
    could u please find and return the best fit row and column index and quantity for the user's query
    
    IMPORTANT MAPPING RULES:
    - Worker Categories (like "Painter", "Carpenter") are mapped to ROW NUMBERS (like "18", "8")
    - Villa/Location names (like "Villa 101", "Villa 102") are mapped to COLUMN LETTERS (like "D", "E")
    - Final cell reference will be: COLUMN_LETTER + ROW_NUMBER (like "D18" for Villa 101 Painter)
    
    IMPORTANT: Return the data in the exact format below:
    row_index: List[str] = Field(description="list of the row numbers (numeric values like '10', '97')")
    columns_index: List[str] = Field(description="list of the column letters (letter values like 'D', 'S', 'T')")
    activity_quantities: List[Tuple[str, str]] = Field(description="list of tuple of the activity quantities with the type (like add updation or replace updation or remove updation)")
    feedbacks: List[str] = Field(description="list of the agent feedback for the user's query just a single feedback for whole query")
    
    CELL REFERENCE FORMAT:
    - columns_index should contain LETTERS (like "D", "S", "T", "AA", "AB")
    - row_index should contain NUMBERS (like "10", "14", "97")
    - Final cell will be: columns_index + row_index (like "D14", "S10", "T97")
    
    OPERATION TYPES - Choose appropriate operation based on user intent:
    - "add": When adding/incrementing labor count (most common for DLR)
    - "replace": When setting exact labor count or correcting previous entries
    - "remove": When clearing/resetting labor count to zero
    
    make sure the feedbacks length should be 1 every time for whole query
    
    EXAMPLES:
    
    ADD Operation (Default - Adding to existing count):
    User: "Painter for Villa 101 has been done for 50 labors"
    # Painter is in row 18, Villa 101 is in column D
    row_index: ["18"]  # Row number for Painter
    columns_index: ["D"]  # Column letter for Villa 101
    activity_quantities: [["50", "add"]]
    feedbacks: ["Painter work done for Villa 101 with 50 labors"]
    
    User: "Grinder for Villa 102 has been done for 100 labors"
    # Grinder is in row 14, Villa 102 is in column E  
    row_index: ["14"]  # Row number for Grinder
    columns_index: ["E"]  # Column letter for Villa 102
    activity_quantities: [["100", "add"]]
    feedbacks: ["Grinder work done for Villa 102 with 100 labors"]
    
    Multiple ADD Operations:
    User: "Carpenter done for Villa 101 and Mason done for Villa 102"
    # Carpenter is in row 8, Villa 101 is in column D; Mason is in row 10, Villa 102 is in column E
    row_index: ["8", "10"]  # Row numbers for Carpenter and Mason
    columns_index: ["D", "E"]  # Column letters for Villa 101 and Villa 102
    activity_quantities: [["100", "add"], ["100", "add"]]
    feedbacks: ["Carpenter done for Villa 101 and Mason done for Villa 102"]
    
    REPLACE Operation (Setting exact count):
    User: "Update Grinder count for Villa 101 to exactly 50 labors"
    row_index: ["14"]
    columns_index: ["D"]
    activity_quantities: [["50", "replace"]]
    feedbacks: ["Grinder count replaced to exactly 50 labors for Villa101"]
    
    REMOVE Operation (Clearing/Resetting):
    User: "Clear all Grinder labors for Villa 101"
    row_index: ["14"]
    columns_index: ["D"]
    activity_quantities: [["0", "remove"]]
    feedbacks: ["Grinder labors cleared for Villa101 removed the values at cell"]
    
    Mixed Operations:
    User: "Add 20 Mason labors for Villa 101, set Grinder to exactly 30 for Villa 102, and clear all Fitter for Villa 103"
    row_index: ["10", "14", "15"]
    columns_index: ["S", "D", "T"]
    activity_quantities: [["20", "add"], ["30", "replace"], ["0", "remove"]]
    feedbacks: ["Mason added 20, Grinder set to 30, Fitter cleared for respective villas"]
    """

def process_logs_query(logs_data: str, users_query: str) -> str:
    return f"""
    here is the data of the logs sheet 
    {logs_data}
    
    here is the user's query
    user's query: {users_query}
    
    based on the user's data please provide the answer very precisely
    """