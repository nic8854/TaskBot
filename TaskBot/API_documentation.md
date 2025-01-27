# API Documentation

## Task JSON Object Syntax
### Example Object
```
{
  "id": 1,
  "name": "Task1",
  "operation": "get",
  "type": "interval",
  "interval": 30,
  "next_execution": "2025-01-27T19:09:56.892221",
  "destination": "https://google.com",
  "payload": null
}
```
### parameters
#### ID
ID of the Task
#### name
Name of the Task
#### operation
Operation of Task to be executed: post, get, patch, delete
#### type
Type of Task: interval, single
#### interval
interval in Seconds
### next_execution
TIme of next execution in ISO-norm (Optional)
#### destination
Url for the task to call; needs to include http or https.
#### payload
Payload string to be sent as a parameter by the task.

## Endpoint
### Tasks
"base-url"/Tasks
