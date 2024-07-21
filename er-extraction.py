import pandas as pd
from dotenv import load_dotenv
import os
from openai import OpenAI
import openai
import json
import time
import tiktoken

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(
  api_key=os.environ['OPENAI_API_KEY'],
)

# Read the CSV file
csv_file = 'ICPSR_DataDictionary_RawData_NIBRS-Incident-Level-2019.csv'
df = pd.read_csv(csv_file)

df['Answer_meaning'] = df['Answer_meaning'].fillna('')

# Concatenate 'Short_Description' and 'Answer_meaning' for each unique 'Question_Code'
df_grouped = df.groupby('Question_Code').agg({
    'Short_Description': 'first',
    'Answer_meaning': lambda x: ' '.join(x)
}).reset_index()

df_grouped['long_description'] = df_grouped['Short_Description'] + ' ' + df_grouped['Answer_meaning']


# Define the base prompt
base_prompt = """
The main purpose of the NSDUH dataset is to provide nationally representative data on the use of tobacco, alcohol, and drugs; substance use disorders; mental health issues; and receipt of substance use and mental health treatment among the civilian, noninstitutionalized population aged 12 or older in the United States. This data allows researchers, clinicians, policymakers, and the general public to better understand and improve the nation’s behavioral health. You are an expert on Ontology and Social Science, and you are currently working on the NSDUH dataset codebook to extract entities for constructing an Ontology. The Ontology is for the topic of "substance abuse, mental health, and rural resilience". Therefore, entities related to substance use, economic status, education, mental health, rural areas, infrastructure, law, and similar topics are relevant and potentially support the reasoning of this research. 

Currently, we have a list of extracted entities and relations. The entities and relations may be extracted from the documents directly, or they may be summarized or categorized in a reasonable way. Please extract entities and relationships that can serve the topic from the following questions in the NSDUH survey sheet:

%s

Please generate the results in JSON format as follows:

{
    "variable": "%s",
    "entities": [
        {
            "entity": "SurveyPeriod",
            "description": "The time frame of the past 30 days, including today's date."
        },
        {
            "entity": "SickOrInjuredDays",
            "description": "Number of whole days missed from school due to sickness or injury."
        },
        {
            "entity": "SchoolAbsenceReason",
            "description": "The reason for missing school, specifically due to being sick or injured."
        },
        {
            "entity": "FamilyCareAbsence",
            "description": "Number of days missed due to staying home with a sick child or family member."
        }
    ],
    "relationships": [
        {
            "relationship": "hasSurveyPeriod",
            "source_entity": "Survey",
            "target_entity": "SurveyPeriod",
            "description": "Relates the survey to the time period of the past 30 days."
        },
        {
            "relationship": "hasSickOrInjuredDays",
            "source_entity": "Respondent",
            "target_entity": "SickOrInjuredDays",
            "description": "Indicates the number of days the respondent missed school due to sickness or injury."
        },
        {
            "relationship": "hasAbsenceReason",
            "source_entity": "SchoolAbsence",
            "target_entity": "SchoolAbsenceReason",
            "description": "Defines the reason for the school absence, such as being sick or injured."
        },
        {
            "relationship": "hasFamilyCareAbsence",
            "source_entity": "Respondent",
            "target_entity": "FamilyCareAbsence",
            "description": "Indicates the number of days the respondent missed school due to caring for a sick child or family member."
        }
    ]
}
"""

# Create the 'jsons' folder if it doesn't exist
if not os.path.exists('jsons'):
    os.makedirs('jsons')

encoding = tiktoken.encoding_for_model("gpt-4o")

def count_tokens(prompt):
    return len(encoding.encode(prompt))


def create_completion_with_retry(client, prompt, token, max_retries=50, delay=2):
    retries = 0
    while retries < max_retries:
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=token+25,
                temperature=0.7
            )
            return response
        except openai.RateLimitError:
            print(f"Rate limit exceeded. Retrying in {delay} seconds...")
            time.sleep(delay)
            retries += 1
            delay *= 2
        except Exception as e:
            print(f"An error occurred: {e}")
            break
    raise Exception("Failed to create completion after several retries")

# Loop through each long description and Question_Code, and send a request to the OpenAI API
results = []

for index, row in df_grouped.iterrows():
    long_description = row['long_description']
    question_code = row['Question_Code']
    
    # Create the complete prompt for each long description and Question_Code
    full_prompt = base_prompt % (long_description, question_code)
    
    print("FuLL PROMPT: ")
    print(full_prompt)
    token_count = count_tokens(full_prompt)
    print(token_count)
    if token_count > 4096:  # GPT-4o token limit
        print(f"Prompt too long for Question_Code {question_code}. Token count: {token_count}")
        continue

    response = create_completion_with_retry(client, full_prompt, token_count)
    
    # Get the generated JSON
    json_output = response.choices[0].message.content
    print(json_output)
    
    # Save the JSON to a file
    file_name = f"jsons/{index}_{question_code}.json"
    with open(file_name, 'w') as f:
        f.write(json_output)
    
    # Append to results
    results.append(json_output)

# Print the results
for result in results:
    print(result)
