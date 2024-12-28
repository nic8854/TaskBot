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


clear()
print("Getting List of Tasks...")
response = make_request(base_url)

clear()

if response:
    # Iterate through the list and print the "name" field
    print("Task Names:")
    iterator = 0
    name_array = []
    for item in response:
        name_array.append(item.get('name'))
        print(f"{iterator+1} = {name_array[iterator]}")
        iterator += 1

task_number = input("Choose Task from List using number or enter 0 to POST: ")
if(task_number == "0"):
    print("You have chosen POST")
    time.sleep(1)
    clear()
    create_name = input("input name: ")
    create_operation = input("input operation: ")
    create_destination = input("input destination: ")
    create_interval = input("input interval: ")
    create_duration = int(input("input duration: "))
    create_log = int(input("input log: "))
    create_task = {
        "name": create_name,
        "operation": create_operation,
        "destination": create_destination,
        "Parameters": {
            "type": create_interval,
            "duration": create_duration,
            "log": create_log
        }
    }
    clear()
    print(f"Your new Task \"{create_name}\"")
    print(json.dumps(create_task, indent=2))
    print("POST is in progress...")
    make_request(base_url, method='POST', data=create_task)
    print("POST is finished")
    exit()

task_number = int(task_number) - 1
if(name_array[task_number] is not None and name_array[task_number] != ""):
    clear()
    chosen_task_name = name_array[task_number]
else:
    print("ERROR")

print(f"getting Data for \"{name_array[task_number]}\"...")

chosen_task_response = make_request(base_url, params={'name': chosen_task_name})
clear()
print(f"Data for \"{name_array[task_number]}\":")

print(json.dumps(chosen_task_response, indent=2))

crud_input = input('0 = leave\n1 = PUT\n2 = DELETE\nWould you like to perform an action on this task?: ')
match crud_input:
    case "0":
        print("You have chosen to leave")
        time.sleep(1)
        exit()
    case "1":
        print("You have chosen PUT")
        time.sleep(1)
        clear()
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
        print("PUT is in progress...")
        make_request(base_url, method='PUT', params={'name': chosen_task_name}, data={param_name : param_value}, echo=1)
        print("PUT is in finished")
    case "2":
        print("You have chosen DELETE")
        time.sleep(1)
        clear()
        print("DELETE is in progress...")
        make_request(base_url, method='DELETE', params={'name': chosen_task_name})
        print("DELETE is in finished")
    case _:
        print("ERROR")

time.sleep(1)
clear()
