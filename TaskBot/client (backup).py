import requests
import json

def make_request(url, method='GET', params=None, data=None, headers=None):

    """
    Args:
        url (str): The endpoint URL.
        method (str): HTTP method ('GET', 'POST', 'PUT', 'DELETE').
        params (dict): Query parameters for the request.
        data (dict): Request body for POST/PUT.
        headers (dict): HTTP headers.
    """
    
    if headers is None:
        headers = {'Content-Type': 'application/json'}

    if data is not None:
        data = json.dumps(data)

    try:
        response = requests.request(method, url, params=params, data=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        print("\n")
        return None
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None

    
# Base URL of the API
base_url = 'http://localhost:8000'

# Test cases
"""
Steps:
    GET All
    GET Task2
    DELETE Task1
    POST Task3
    Update Task2
    GET All
"""

print("=== GET all tasks ===")
make_request(f"{base_url}/tasks")

print("=== GET a specific task ===")
make_request(f"{base_url}/tasks", params={'name': 'Task2'})

print("=== DELETE a specific task ===")
make_request(f"{base_url}/tasks", method='DELETE', params={'name': 'Task1'})
make_request(f"{base_url}/tasks", params={'name': 'Task1'})

print("=== POST a new task ===")
new_task = {
    "name": "Task3",
    "operation": "post",
    "destination": "http://example.com/api",
    "Parameters": {
        "type": "random",
        "duration": 120,
        "log": 1
    }
}
make_request(f"{base_url}/tasks", method='POST', data=new_task)

print("=== UPDATE a specific task ===")
updated_task = {
    "operation": "put",
    "destination": "http://updated.example.com/api",
    "Parameters": {
        "type": "burst",
        "duration": 90,
        "log": 1
    }
}
make_request(f"{base_url}/tasks", method='PUT', params={'name': 'Task2'}, data=updated_task)

print("=== GET all tasks ===")
make_request(f"{base_url}/tasks")