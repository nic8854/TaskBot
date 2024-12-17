import http.server
import socketserver
import json
from urllib.parse import urlparse, parse_qs
from requests import Response
        
database = {
    "task_db": [
        {
            "name": "Task1",
            "operation": "get",
            "destination": "http://localhost:800",
            "Parameters": {
                "type": "interval",
                "duration": 30,
                "log": 1
            }
        },        
        {
            "name": "Task2",
            "operation": "get",
            "destination": "http://google.com",
            "Parameters": {
                "type": "burst",
                "duration": 60,
                "log": 0
            }
        }
    ]
}

class MyHandler(http.server.SimpleHTTPRequestHandler):

    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def _read_content(self):
        try:
            content_length = int(self.headers['Content-Length'])
            return self.rfile.read(content_length)
        except ValueError:
            return None
    
    # function to get the query parameters
    def get_tasks(self, task_name=None):
        data = database['task_db']
        if task_name:
            return next((task for task in data if task['name'] == task_name), None)
        return data
    
    # function to handle POST (create) requests
    def do_POST(self):
        if self.path == '/tasks':
            try:
                task_data = json.loads(self._read_content())
                if any(t['name'] == task_data['name'] for t in database['task_db']):
                    self._set_headers(409)
                    self.wfile.write(json.dumps({"error": "Task already exists"}).encode())
                else:
                    database['task_db'].append(task_data)
                    self._set_headers(201)
                    self.wfile.write(json.dumps({"message": "Task added"}).encode())
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid data", "details": str(e)}).encode())
 
    # function to handle GET (read) requests
    def do_GET(self):
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        if parsed_path.path == '/tasks':
            task_name = query.get('name', [None])[0]
            tasks = self.get_tasks(task_name)
            if task_name and not tasks:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Task not found"}).encode())
            else:
                self._set_headers(200)
                self.wfile.write(json.dumps(tasks).encode())

    # function to handle PUT (update) requests
    def do_PUT(self):
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        if parsed_path.path == '/tasks':
            task_name = query.get('name', [None])[0]
            task_data = self._read_content()
            task = self.get_tasks(task_name)
            if task:
                try:
                    # Update the task in the database
                    updated_task = json.loads(task_data)
                    task.update(updated_task)
                    self._set_headers(200)
                    self.wfile.write(json.dumps({"message": "Task updated"}).encode())
                except Exception as e:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Invalid data", "details": str(e)}).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Task not found"}).encode())
    
    # function to handle DELETE (delete) requests
    def do_DELETE(self):
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        if parsed_path.path == '/tasks':
            task_name = query.get('name', [None])[0]
            task = self.get_tasks(task_name)
            if task:
                # Remove the task from the database by rewriting all tasks except the one to be deleted
                database['task_db'] = [t for t in database['task_db'] if t['name'] != task_name]
                self._set_headers(200)
                self.wfile.write(json.dumps({"message": "Task deleted"}).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Task not found"}).encode())

# define Port
PORT = 8000

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
