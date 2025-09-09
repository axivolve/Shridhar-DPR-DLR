from agno.agent import Agent
from agno.models.groq import Groq
from pydantic import BaseModel, Field
from dotenv import load_dotenv 
from app.config import SYSTEM_PROMPT_DPR, SYSTEM_PROMPT_LOGS, SYSTEM_PROPMT_DLR
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

REGULAR EXAMPLES:
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

these are the examples which i'm getting the output of the llm so you should give the output in the same manner
"""
    

def prompt_builder_for_dlr_updation(column_name: str, row_data: str, users_query: str) -> str:
    return f"""
    here is the data of the sheet which is associated with it's indexing
    here is the data from column {column_name}
    here is the data from row {row_data}
    
    aand here is the user's query
    user's query: {users_query}
    
    could u please find and return the best fit row and column index and quantity for the user's query
    
    IMPORTANT: Return the data in the exact format below:
    row_index: List[str] = Field(description="list of the row numbers (numeric values like '10', '97')")
    columns_index: List[str] = Field(description="list of the column letters (letter values like 'D', 'S', 'T')")
    quantities: List[float] = Field(description="list of the quantities mentioned in the user's query")   
    feedbacks: List[str] = Field(description="list of the agent feedback for the user's query just a single feedback for whole query")
    
    CELL REFERENCE FORMAT:
    - columns_index should contain LETTERS (like "D", "S", "T", "AA", "AB")
    - row_index should contain NUMBERS (like "10", "14", "97")
    - Final cell will be: columns_index + row_index (like "D14", "S10", "T97")
    
    make sure the feedbacks length should be 1 every time for whole query
    
    example :
    User: "Grinder for Villa 101 has been done for 100 labors"
    row_index: ["14"]  # Row number
    columns_index: ["D"]  # Column letter  
    quantities: [100.0]
    feedbacks: ["Grinder done for Villa101 with 100 labors"]
    
    example :
    User: "Fitter done for Villa 101 and Mason done for Villa 102"
    row_index: ["10", "97"]  # Row numbers
    columns_index: ["S", "T"]  # Column letters
    quantities: [100.0, 100.0]
    feedbacks: ["Fitter done for Villa101 and Mason done for Villa102"]
    """

def process_logs_query(logs_data: str, users_query: str) -> str:
    return f"""
    here is the data of the logs sheet 
    {logs_data}
    
    here is the user's query
    user's query: {users_query}
    
    based on the user's data please provide the answer very precisely 
    and if the user has asked for the analystics nd all then provide the answer in Tabular format
    """