import json
import requests
import os
from openai import OpenAI
from assistant_insturctions import assistant_instructions
from dotenv import load_dotenv, dotenv_values

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")

# Init OpenAI Client
client = OpenAI(
    api_key=OPENAI_API_KEY,
    default_headers={"OpenAI-Beta": "assistants=v2"}
)
# Add lead to Airtable
def create_lead(name="", company_name="", phone="", email=""):
  url = "https://api.airtable.com/v0/appfzL1swEyGx2aYV/Leads"  # Change this to your Airtable API URL
  headers = {
      "Authorization" : 'Bearer ' + AIRTABLE_API_KEY,
      "Content-Type": "application/json"
  }
  data = {
      "records": [{
          "fields": {
              "Name": name,
              "Phone": phone,
              "Email": email,
              "CompanyName": company_name,
          }
      }]
  }
  response = requests.post(url, headers=headers, json=data)
  if response.status_code == 200:
    print("Lead created successfully.")
    return response.json()
  else:
    print(f"Failed to create lead: {response.text}")

def create_assistant(client):
    assistant_file_path = 'assistant.json'

    # Eğer daha önce oluşturulmuş bir assistant varsa, yükle
    if os.path.exists(assistant_file_path):
        with open(assistant_file_path, 'r') as file:
            assistant_data = json.load(file)
            assistant_id = assistant_data['assistant_id']
            print("Loaded existing assistant ID.")
    else:
        # Eğer assistant.json yoksa, yeni bir assistant oluştur
        assistant = client.beta.assistants.create(
            instructions=assistant_instructions,
            model="gpt-4-turbo-preview",
            tools=[
                {"type": "file_search"},
                {"type": "function", "function": {
                    "name": "create_lead",
                    "description": "Capture lead details and save to Airtable.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Name of the lead."},
                            "phone": {"type": "string", "description": "Phone number of the lead."},
                            "email": {"type": "string", "description": "Email of the lead."},
                            "company_name": {"type": "string", "description": "Company name of the lead."}
                        },
                        "required": ["name", "email", "company_name"]
                    }
                }}
            ]
        )

        with open(assistant_file_path, 'w') as file:
            json.dump({'assistant_id': assistant.id}, file)
            print("Created a new assistant and saved the ID.")

        assistant_id = assistant.id

    return assistant_id
