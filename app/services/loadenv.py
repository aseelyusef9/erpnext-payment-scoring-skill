import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read variables safely
base_url = os.getenv("ERP_BASE_URL")
api_token = os.getenv("ERP_API_TOKEN")

if not base_url or not api_token:
    raise Exception("Missing ERPNext environment variables")

headers = {
    "Authorization": f"token {api_token}",
    "Content-Type": "application/json"
}

