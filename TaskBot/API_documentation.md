# API Documentation

## Task JSON Object Syntax
### Example Object
```
{
"name" : "Task1",
"operation" : "get",
"destination" : "http://localhost:8000",
  "Parameters" {
  "type" : "interval",
  "duration" : 60,
  "log" : 0
  }
}
```
### Parameters
#### Name
Name of the Task
#### Operation
Kind of Task: post, get, patch, delete
#### Destination
Url of desired Destination including Port
#### Type
Type of Task: interval, singleshot, onresponse
#### Duration
Duration in Seconds
#### Log
Log output as boolean: 0, 1

## Endpoints
### Tasks
/Tasks
### Log
/Log