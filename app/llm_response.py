from agno.agent import Agent
from agno.models.groq import Groq
from pydantic import BaseModel, Field
from dotenv import load_dotenv 
from app.config import SYSTEM_PROMPT_DPR
from app.models import DPRUpdationResult

def get_support_agent(api_key: str) -> Agent:
    return Agent(
        model=Groq(id="meta-llama/llama-4-scout-17b-16e-instruct", api_key=api_key),
        system_message=SYSTEM_PROMPT_DPR,
        markdown=False,
        response_model=DPRUpdationResult,
        retries=10,
        add_datetime_to_instructions=True,
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
    
