import requests
import json

#hallihallo

def make_request(url, method='GET', params=None, data=None, headers=None):
    """
    Sends an HTTP request and prints the response.

    Args:
        url (str): The endpoint URL.
        method (str): The HTTP method (GET, POST, PUT, DELETE).
        params (dict): URL query parameters.
        data (dict): Request body payload.
        headers (dict): HTTP headers.
    """
    if headers is None:
        headers = {'Content-Type': 'application/json'}

    if data is not None:
        data = json.dumps(data)

    try:
        response = requests.request(method, url, params=params, data=data, headers=headers)
        print(f"Request: {method} {url}")
        if params:
            print(f"Params: {params}")
        if data:
            print(f"Data: {data}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        print("\n")
    except requests.RequestException as e:
        print(f"Error during request: {e}")


base_url = 'http://localhost:8000/tasks'

# Step 1: Create two tasks
print("STEP 1: Create Task 1")
task_1 = {
    "name": "Task1",
    "operation": "get",
    "destination": "http://example.com/task1",
    "Parameters": {
        "type": "interval",
        "duration": 30,
        "log": 1
    }
}
make_request(base_url, method='POST', data=task_1)

print("STEP 1: Create Task 2")
task_2 = {
    "name": "Task2",
    "operation": "post",
    "destination": "http://example.com/task2",
    "Parameters": {
        "type": "burst",
        "duration": 60,
        "log": 0
    }
}
make_request(base_url, method='POST', data=task_2)

# Step 2: Read all tasks
print("STEP 2: Read all tasks")
make_request(base_url)

# Step 3: Update Task 2
print("STEP 3: Update Task 2")
updated_task_2 = {
    "operation": "put",
    "destination": "http://example.com/task2/updated",
    "Parameters": {
        "type": "random",
        "duration": 45,
        "log": 1
    }
}
make_request(base_url, method='PUT', params={'name': 'Task2'}, data=updated_task_2)

# Step 4: Read Task 2
print("STEP 4: Read Task 2")
make_request(base_url, params={'name': 'Task2'})

# Step 5: Delete Task 2
print("STEP 5: Delete Task 2")
make_request(base_url, method='DELETE', params={'name': 'Task2'})

# Step 6: Verify Task 2 Deletion
print("STEP 6: Verify Task 2 Deletion")
make_request(base_url, params={'name': 'Task2'})

# Step 7: Read all tasks again
print("STEP 7: Read all tasks after deletion")
make_request(base_url)
