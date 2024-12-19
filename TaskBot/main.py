import http.server
import socketserver
import json
import sqlite3
from urllib.parse import urlparse, parse_qs
import threading
import time
from datetime import datetime, timedelta
import requests

# Initialize SQLite Database
DATABASE_FILE = "tasks.db"

def init_db():
    # Initialize the SQLite database and create the tasks table if not exists.
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            operation TEXT NOT NULL,
            type TEXT NOT NULL,
            interval INTEGER,
            next_execution TEXT,
            destination TEXT NOT NULL,
            payload TEXT
        )
        """)
        conn.commit()


class TaskScheduler:
    def __init__(self, database_file):
        self.database_file = database_file
        self.running = True

    def fetch_due_tasks(self):
        # Fetch tasks that are due for execution.
        with sqlite3.connect(self.database_file) as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            # Parse next_execution as ISO 8601 before comparing
            def parse_isoformat(next_execution):
                try:
                    return datetime.fromisoformat(next_execution)
                except ValueError:
                    raise ValueError(f"Invalid date format: {next_execution}")
            
            cursor.execute("""
            SELECT id, name, operation, type, interval, destination, payload, next_execution
            FROM tasks
            """)
            
            # Filter the tasks in Python
            all_tasks = cursor.fetchall()
            due_tasks = [
                task for task in all_tasks
                if parse_isoformat(task[-1]) <= datetime.fromisoformat(now)
            ]
            return due_tasks

    def execute_task(self, task):
        # Execute the task and update the database accordingly.
        task_id, name, operation, task_type, interval, destination, payload, next_execution = task
        print(f"Executing task: {name}")

        try:
            # Perform the task operation
            success = self.make_request(destination, method=operation, data=payload)

            # Update task schedule
            with sqlite3.connect(self.database_file) as conn:
                cursor = conn.cursor()
                if task_type == 'interval':
                    next_exec_time = datetime.now() + timedelta(seconds=int(interval))
                    print("Next execution time:", next_exec_time.isoformat())
                    cursor.execute("""
                    UPDATE tasks SET next_execution = ? WHERE id = ?
                    """, (next_exec_time.isoformat(), task_id))
                elif task_type == 'single' and success:
                    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                conn.commit()
        except Exception as e:
            print(f"Error executing task {name}: {e}")

    def make_request(self,url, method=None, params=None, data=None, headers=None):
        """
        Sends an HTTP request and prints the response.
        Args:
            url (str): The endpoint URL.
            method (str): The HTTP method (GET, POST, PUT, DELETE).
            params (dict): URL query parameters.
            data (dict/str): Request body payload.
            headers (dict): HTTP headers.
        """

        if headers is None:
            headers = {'Content-Type': 'application/json'}
        if isinstance(data, dict):  # Ensure the payload is serialized if it's a dictionary
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
            return  True
        except requests.RequestException as e:
            print(f"Error during request: {e}")
            return  False

    def task_execution_loop(self):
        # Continuously check and execute due tasks.
        print("Task Scheduler running...")
        # TODO: Add a way to stop the scheduler
        while self.running:
            try:
                due_tasks = self.fetch_due_tasks()
                for task in due_tasks:
                    print("Current time:", datetime.now().isoformat(), "vs Next execution time:", task[7])
                    self.execute_task(task)
            except Exception as e:
                print(f"Error in task execution loop: {e}")
            time.sleep(1)  # Check for tasks every second



class MyHandler(http.server.SimpleHTTPRequestHandler):
    def _set_headers(self, status_code=200):
        # Set HTTP headers with the specified status code.
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def _read_content(self):
        # Read and parse the request body.
        content_length = int(self.headers.get('Content-Length', 0))
        return self.rfile.read(content_length).decode('utf-8')

    def fetch_tasks(self, task_name=None):
        # Fetch tasks from the database.
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            if task_name:
                cursor.execute("SELECT * FROM tasks WHERE name = ?", (task_name,))
                return cursor.fetchone()
            else:
                cursor.execute("SELECT * FROM tasks")
                return cursor.fetchall()

    def add_task(self, task_data):
        # Add a task to the database.
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            try:
                # Set default values for interval and next_execution
                interval = task_data.get("interval")
                if interval is None:
                    interval = 600  # default to 10 minutes if interval is None
                next_execution = task_data.get("next_execution")
                if next_execution is None:
                    next_execution = datetime.now().isoformat()

                cursor.execute("""
                INSERT INTO tasks (name, operation, type, interval, next_execution, destination, payload)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    task_data["name"],
                    task_data["operation"],
                    task_data["type"],
                    interval,
                    next_execution,
                    task_data["destination"],
                    task_data.get("payload", None)
                ))
                conn.commit()
                return True, None
            except sqlite3.IntegrityError as e:
                return False, str(e)

    def update_task(self, task_name, task_data):
        # Update an existing task in the database.
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE tasks
            SET operation = ?, type = ?, interval = ?, next_execution = ?, destination = ?, payload = ?
            WHERE name = ?
            """, (
                task_data["operation"],
                task_data["type"],
                task_data["interval"],
                task_data["next_execution"],
                task_data["destination"],
                task_data.get("payload", None),
                task_name
            ))
            conn.commit()
            return cursor.rowcount > 0

    def delete_task(self, task_name):
        # Delete a task from the database.
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE name = ?", (task_name,))
            conn.commit()
            return cursor.rowcount > 0


    def do_POST(self):
        # Handle POST requests to add a new task.
        if self.path == '/tasks':
            try:
                task_data = json.loads(self._read_content())
                success, error = self.add_task(task_data)
                if success:
                    self._set_headers(201)
                    self.wfile.write(json.dumps({"message": "Task added"}).encode())
                else:
                    self._set_headers(409)
                    self.wfile.write(json.dumps({"error": error}).encode())
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid data", "details": str(e)}).encode())

    def do_GET(self):
        # Handle GET requests to retrieve tasks.
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        if parsed_path.path == '/tasks':
            task_name = query.get('name', [None])[0]
            if task_name:
                task = self.fetch_tasks(task_name)
                if task:
                    self._set_headers(200)
                    self.wfile.write(json.dumps({
                        "id": task[0], "name": task[1], "operation": task[2], "type": task[3],
                        "interval": task[4], "next_execution": task[5], "destination": task[6], "payload": task[7]
                    }).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Task not found"}).encode())
            else:
                tasks = self.fetch_tasks()
                self._set_headers(200)
                self.wfile.write(json.dumps([
                    {
                        "id": t[0], "name": t[1], "operation": t[2], "type": t[3],
                        "interval": t[4], "next_execution": t[5], "destination": t[6], "payload": t[7]
                    } for t in tasks
                ]).encode())

    def do_PUT(self):
        # Handle PUT requests to update a task.
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        if parsed_path.path == '/tasks':
            task_name = query.get('name', [None])[0]
            if task_name:
                task_data = json.loads(self._read_content())
                success = self.update_task(task_name, task_data)
                if success:
                    self._set_headers(200)
                    self.wfile.write(json.dumps({"message": "Task updated"}).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Task not found"}).encode())

    def do_DELETE(self):
        # Handle DELETE requests to remove a task.
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        if parsed_path.path == '/tasks':
            task_name = query.get('name', [None])[0]
            if task_name:
                success = self.delete_task(task_name)
                if success:
                    self._set_headers(200)
                    self.wfile.write(json.dumps({"message": "Task deleted"}).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Task not found"}).encode())


# Initialize the database
init_db()

# Start the Task Scheduler
scheduler = TaskScheduler(DATABASE_FILE)
execution_thread = threading.Thread(target=scheduler.task_execution_loop, daemon=True)
execution_thread.start()

# Start the server
PORT = 8000
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
