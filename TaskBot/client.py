import requests
import json
import os
import time

clear = lambda: os.system('cls')

def make_request(url, method='GET', params=None, data=None, headers=None, echo=0):
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
        if(echo):
            print(f"Request: {method} {url}")
        if params:
            if(echo):
                print(f"Params: {params}")
        if data:
            if(echo):
                print(f"Data: {data}")
        if(echo):
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            print("\n")
        return json.loads(response.text)
    except requests.RequestException as e:
        print(f"Error during request: {e}")


base_url = 'http://localhost:8000/tasks'



response = make_request(base_url)
#print("response:")
#print(response)
if response:
    # Iterate through the list and print the "name" field
    print("Task Names:")
    iterator = 0
    name_array = []
    for item in response:
        name_array.append(item.get('name'))
        print(f"{iterator+1} = {name_array[iterator]}")
        iterator += 1

task_number = input("Choose Task from List using number or enter 0 to CREATE: ")
task_number = int(task_number) - 1
if(name_array[task_number] is not None and name_array[task_number] != ""):
    print(f"\nYou chose: {name_array[task_number]}")
    chosen_task_name = name_array[task_number]
else:
    print("ERROR")

print("GET request executing...\n")

chosen_task_response = make_request(base_url, params={'name': chosen_task_name})
clear()
print(f"Data for {name_array[task_number]}")

print(json.dumps(chosen_task_response, indent=2))

crud_input = input('0 = leave\n1 = PUT\n2 = DELETE\nWould you like to perform an action on this task?: ')
match crud_input:
    case "0":
        print("You have chosen to leave")
        exit()
    case "1":
        time.sleep(1)
        clear()

        print("You have chosen PUT")
        print(f"Data for {name_array[task_number]}")
        print(json.dumps(chosen_task_response, indent=2))

        if chosen_task_response:
            param_iterator = 0
            param_array = []
            for item in chosen_task_response:
                param_array.append(item)
                print(f"{param_iterator+1} = {param_array[param_iterator]}")
                param_iterator += 1

        param_number = input("Choose which parameter to change: ")
        param_number = int(param_number) - 1
        param_name = param_array[param_number]

        param_value = input("Enter value: ")

        make_request(base_url, method='PUT', params={'name': chosen_task_name}, data={param_name : param_value}, echo=1)
    case "2":
        print("You have chosen DELETE")
        make_request(base_url, method='DELETE', params={'name': chosen_task_name})
    case _:
        print("ERROR")

time.sleep(1)
clear()


"""
# Step 1: Create two tasks
print("STEP 1: Create Task 1")
task_1 = {
    "name": "Task3",
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
    "name": "Task4",
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
response = make_request(base_url)
print(response)


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


crud_input = input('Which operation would you like to perform?\n1 = GET (default)\n2 = PUT\n3 = POST\n4 = DELETE\n')
match crud_input:
    case "1":
        print("You have chosen GET")
    case "2":
        print("You have chosen PUT")
    case "3":
        print("You have chosen POST")
    case "4":
        print("You have chosen DELETE")
    case _:
        print("You have chosen GET")

"""