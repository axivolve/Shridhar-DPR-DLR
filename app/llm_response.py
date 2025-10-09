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
    - ONLY use exact matches from the provided data - no assumptions or guesses
    - If you cannot find an exact or close fuzzy match, return error response
    - LANGUAGE FLEXIBILITY: Recognize worker categories and villa numbers regardless of language (English/Hindi/Gujarati/phonetic)
    - PHONETIC MATCHING: Match based on sound/meaning, not exact spelling (e.g., "meson" = "Mason", "vila" = "Villa")
    
    IMPORTANT: Return the data in the exact format below:
    row_index: List[str] = Field(description="list of the row numbers (numeric values like '10', '97') - EMPTY if no valid match found")
    columns_index: List[str] = Field(description="list of the column letters (letter values like 'D', 'S', 'T') - EMPTY if no valid match found")
    activity_quantities: List[Tuple[str, str]] = Field(description="list of tuple of the activity quantities with the type (like add updation or replace updation or remove updation) - EMPTY if no valid match found")
    feedbacks: List[str] = Field(description="list of the agent feedback for the user's query just a single feedback for whole query - ALWAYS provide feedback even for errors")
    
    VALIDATION REQUIREMENTS:
    1. ONLY use worker categories that exist in the provided WORKER CATEGORIES data
    2. ONLY use villa/locations that exist in the provided VILLA/LOCATION data
    3. If either worker category OR villa/location is not found, return empty arrays
    4. Always provide exactly 1 feedback message
    5. For errors, explain what was not found and suggest checking the available options
    
    MULTILINGUAL & PHONETIC SUPPORT:
    The system should recognize worker categories and villa numbers in multiple languages and phonetic spellings:
    
    WORKER CATEGORY TRANSLATIONS & PHONETIC VARIATIONS:
    - Carpenter: कारपेंटर, કારપેન્ટર, carpenter, karpentar, karpenter
    - Mason: मेसन, મેસન, mason, meson, maisan
    - Painter: पेंटर, પેન્ટર, painter, pentar, penter
    - Plumber: प्लंबर, પ્લમ્બર, plumber, plambar, plumbar
    - Electrician: इलेक्ट्रिशियन, ઇલેક્ટ્રિશિયન, electrician, elektrishan, bijli wala
    - Welder: वेल्डर, વેલ્ડર, welder, veldar, weldar
    - Grinder: ग्राइंडर, ગ્રાઇન્ડર, grinder, graindar, grinder
    - Fitter: फिटर, ફિટર, fitter, fitar, phitar
    - Helper: हेल्पर, હેલ્પર, helper, helpar, sahayak, मदद करने वाला
    
    VILLA/LOCATION TRANSLATIONS:
    - Villa: विला, વિલા, villa, vila, vela
    - Numbers: 101 = एक सौ एक, એક સો એક, ek sau ek, eksauek
    - Common patterns: "Villa 101", "विला 101", "વિલા 101", "vila 101", "vela 101"
    
    NUMBER RECOGNITION:
    - Support both numeric (101, 102) and word forms (ek sau ek, do sau do)
    - Hindi numbers: एक (1), दो (2), तीन (3), चार (4), पांच (5), etc.
    - Gujarati numbers: એક (1), બે (2), ત્રણ (3), ચાર (4), પાંચ (5), etc.
    - Common quantity words: majdur, majur, मजदूर, મજૂર, laborers, workers, log, लोग, લોકો
    
    FUZZY MATCHING PRINCIPLES:
    - Match based on phonetic similarity, not exact spelling
    - Recognize common misspellings and transliterations
    - Be flexible with word order (Hindi/Gujarati grammar vs English)
    - Extract numbers from mixed language contexts
    
    CELL REFERENCE FORMAT:
    - columns_index should contain LETTERS (like "D", "S", "T", "AA", "AB")
    - row_index should contain NUMBERS (like "10", "14", "97")
    - Final cell will be: columns_index + row_index (like "D14", "S10", "T97")
    
    OPERATION TYPES - Choose appropriate operation based on user intent:
    - "add": When adding/incrementing labor count (most common for DLR)
    - "replace": When setting exact labor count or correcting previous entries
    - "remove": When clearing/resetting labor count to zero
    
    make sure the feedbacks length should be 1 every time for whole query
    
    ERROR HANDLING:
    If the user asks for worker categories or villa/locations that don't exist in the provided data:
    - Return empty lists for row_index, columns_index, and activity_quantities
    - Provide a helpful error message in feedbacks explaining what's missing
    
    ERROR EXAMPLES:
    
    User: "Update Engineer work for Villa 101 with 50 labors"
    # "Engineer" is not in the worker categories list
    row_index: []
    columns_index: []
    activity_quantities: []
    feedbacks: ["Unable to find 'Engineer' in the worker categories. Available categories are: Carpenter, Barbender, Mason, Forman, Fitter, Welder, Grinder, Rigger, Gas Cutter, Electrician, Painter, Plumber, Scaffolders, Flooring (Mason), Aluminium, Water Proofing, Helper."]
    
    User: "Update Painter work for Villa 999 with 30 labors"
    # "Villa 999" is not in the villa/location list
    row_index: []
    columns_index: []
    activity_quantities: []
    feedbacks: ["Unable to find 'Villa 999' in the location data. Please check the villa number and try again with a valid villa from the available list."]
    
    User: "Update Engineer work for Villa 999 with 40 labors"
    # Both "Engineer" and "Villa 999" don't exist
    row_index: []
    columns_index: []
    activity_quantities: []
    feedbacks: ["Unable to find 'Engineer' in worker categories and 'Villa 999' in location data. Please provide valid worker category and villa number from the available options."]
    
    User: "Update some random work for some place with numbers"
    # Completely unrelated input
    row_index: []
    columns_index: []
    activity_quantities: []
    feedbacks: ["Unable to identify valid worker category and villa location from your request. Please specify a valid worker type and villa number from the available data."]
    
    EXAMPLES:
    
    ADD Operation (Default - Adding to existing count):
    User: "Painter for Villa 101 has been done for 50 labors"
    # Painter is in row 18, Villa 101 is in column D
    row_index: ["18"]  # Row number for Painter
    columns_index: ["D"]  # Column letter for Villa 101
    activity_quantities: [["50", "add"]]
    feedbacks: ["Painter work done for Villa 101 with 50 labors"]
    
    MULTILINGUAL EXAMPLES:
    
    User: "विला 101 के लिए 40 मजदूरों द्वारा मेसन का काम"
    # Hindi: "Mason work for Villa 101 with 40 laborers"
    # Mason is in row 10, Villa 101 is in column D
    row_index: ["10"]
    columns_index: ["D"]
    activity_quantities: [["40", "add"]]
    feedbacks: ["Mason work completed for Villa 101 with 40 laborers"]
    
    User: "વિલા 102 માટે પેન્ટર કામ 30 મજૂર"
    # Gujarati phonetic: "Villa 102 mate painter kam 30 majur"
    # Painter is in row 18, Villa 102 is in column E
    row_index: ["18"]
    columns_index: ["E"]
    activity_quantities: [["30", "add"]]
    feedbacks: ["Painter work completed for Villa 102 with 30 laborers"]
    
    User: "vila 103 ke liye karpentar ka kam 25 majdur se"
    # Hindi phonetic: "Carpenter work for Villa 103 with 25 laborers"
    # Carpenter is in row 8, Villa 103 is in column F
    row_index: ["8"]
    columns_index: ["F"]
    activity_quantities: [["25", "add"]]
    feedbacks: ["Carpenter work completed for Villa 103 with 25 laborers"]
    
    User: "ग्राइंडर विला 104 के लिए 50 मजदूर"
    # Hindi: "Grinder for Villa 104 with 50 laborers"
    # Grinder is in row 14, Villa 104 is in column G
    row_index: ["14"]
    columns_index: ["G"]
    activity_quantities: [["50", "add"]]
    feedbacks: ["Grinder work completed for Villa 104 with 50 laborers"]
    
    User: "Grinder for Villa 102 has been done for 100 labors"
    # Grinder is in row 14, Villa 102 is in column E  
    row_index: ["14"]  # Row number for Grinder
    columns_index: ["E"]  # Column letter for Villa 102
    activity_quantities: [["100", "add"]]
    feedbacks: ["Grinder work done for Villa 102 with 100 labors"]
    
    PHONETIC & MIXED LANGUAGE EXAMPLES:
    
    User: "plumber vila 105 mai 20 majur ka kam"
    # Mixed Hindi-English phonetic: "Plumber work in Villa 105 with 20 laborers"
    # Plumber is in row 19, Villa 105 is in column H
    row_index: ["19"]
    columns_index: ["H"]
    activity_quantities: [["20", "add"]]
    feedbacks: ["Plumber work completed for Villa 105 with 20 laborers"]
    
    User: "weldar ka kam vila 106 ke liye 35 log"
    # Hindi phonetic: "Welder work for Villa 106 with 35 people"
    # Welder is in row 13, Villa 106 is in column I
    row_index: ["13"]
    columns_index: ["I"]
    activity_quantities: [["35", "add"]]
    feedbacks: ["Welder work completed for Villa 106 with 35 laborers"]
    
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
    
    COMPREHENSIVE ERROR EXAMPLES:
    
    User: "Update Doctor work for Villa 101 with 25 labors"
    # "Doctor" is not a valid worker category
    row_index: []
    columns_index: []
    activity_quantities: []
    feedbacks: ["Unable to find 'Doctor' in the available worker categories. Please use valid categories like Carpenter, Painter, Mason, etc."]
    
    User: "डॉक्टर का काम विला 101 के लिए 30 मजदूर"
    # Hindi: "Doctor work for Villa 101 with 30 laborers" - invalid worker category
    row_index: []
    columns_index: []
    activity_quantities: []
    feedbacks: ["Unable to find 'Doctor' in the available worker categories. Please use valid categories like Carpenter, Painter, Mason, etc."]
    
    User: "Update Painter work for Building 999 with 30 labors"
    # "Building 999" is not a valid location
    row_index: []
    columns_index: []
    activity_quantities: []
    feedbacks: ["Unable to find 'Building 999' in the available locations. Please use valid villa numbers or locations from the sheet data."]
    
    User: "પેન્ટર કામ વિલા 999 માટે 25 મજૂર"
    # Gujarati: "Painter work for Villa 999 with 25 laborers" - invalid villa number
    row_index: []
    columns_index: []
    activity_quantities: []
    feedbacks: ["Unable to find 'Villa 999' in the available locations. Please use valid villa numbers or locations from the sheet data."]
    
    User: "I want to order pizza for lunch"
    # Completely unrelated to construction work
    row_index: []
    columns_index: []
    activity_quantities: []
    feedbacks: ["This request is not related to DLR sheet updates. Please provide worker category, villa location, and labor quantity for valid updates."]
    
    User: "Update xyz work for abc place with def numbers"
    # Unclear/invalid input
    row_index: []
    columns_index: []
    activity_quantities: []
    feedbacks: ["Unable to identify valid worker category, villa location, or quantity from your request. Please specify clearly using available data."]
    """

def process_logs_query(logs_data: str, users_query: str) -> str:
    return f"""
    here is the data of the logs sheet 
    {logs_data}
    
    here is the user's query
    user's query: {users_query}
    
    based on the user's data please provide the answer very precisely
    """