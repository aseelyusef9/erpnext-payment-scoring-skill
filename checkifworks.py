
import requests
from services import base_url
from services import api_token
from services import headers


# GET Customers
response = requests.get(
    f"{base_url}/api/resource/Customer",
    headers=headers
)

if response.status_code == 200:
    print("Customers:")
    for customer in response.json()["data"]:
        print(customer)
else:
    print("Error:", response.status_code, response.text)

# POST new Customer
new_customer = {
    "customer_name": "John Doe",
    "customer_type": "Individual",
    "territory": "All Territories"
}

response = requests.post(
    f"{base_url}/api/resource/Customer",
    headers=headers,
    json=new_customer
)

if response.status_code in (200, 201):
    print("New Customer Created:", response.json())
else:
    print("Error creating customer:", response.text)
