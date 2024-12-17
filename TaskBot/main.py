import http.server
import socketserver
import json
import sqlite3
from urllib.parse import urlparse, parse_qs

# Initialize SQLite Database
DATABASE_FILE = "tasks.db"

def init_db():
    """Initialize the SQLite database and create the tasks table if not exists."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            operation TEXT NOT NULL,
            destination TEXT NOT NULL,
            parameters TEXT NOT NULL
        )
        """)
        conn.commit()

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def _set_headers(self, status_code=200):
        """Set HTTP headers with the specified status code."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def _read_content(self):
        """Read and parse the request body."""
        content_length = int(self.headers.get('Content-Length', 0))
        return self.rfile.read(content_length).decode('utf-8')

    def fetch_tasks(self, task_name=None):
        """Fetch tasks from the database."""
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            if task_name:
                cursor.execute("SELECT * FROM tasks WHERE name = ?", (task_name,))
                return cursor.fetchone()
            else:
                cursor.execute("SELECT * FROM tasks")
                return cursor.fetchall()

    def add_task(self, task_data):
        """Add a task to the database."""
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                INSERT INTO tasks (name, operation, destination, parameters)
                VALUES (?, ?, ?, ?)
                """, (task_data["name"], task_data["operation"], task_data["destination"], json.dumps(task_data["Parameters"])))
                conn.commit()
                return True, None
            except sqlite3.IntegrityError as e:
                return False, str(e)

    def update_task(self, task_name, task_data):
        """Update an existing task in the database."""
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE tasks
            SET operation = ?, destination = ?, parameters = ?
            WHERE name = ?
            """, (task_data["operation"], task_data["destination"], json.dumps(task_data["Parameters"]), task_name))
            conn.commit()
            return cursor.rowcount > 0

    def delete_task(self, task_name):
        """Delete a task from the database."""
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE name = ?", (task_name,))
            conn.commit()
            return cursor.rowcount > 0

    def do_POST(self):
        """Handle POST requests to add a new task."""
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
        """Handle GET requests to retrieve tasks."""
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        if parsed_path.path == '/tasks':
            task_name = query.get('name', [None])[0]
            if task_name:
                task = self.fetch_tasks(task_name)
                if task:
                    self._set_headers(200)
                    self.wfile.write(json.dumps({
                        "id": task[0], "name": task[1], "operation": task[2],
                        "destination": task[3], "Parameters": json.loads(task[4])
                    }).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Task not found"}).encode())
            else:
                tasks = self.fetch_tasks()
                self._set_headers(200)
                self.wfile.write(json.dumps([
                    {"id": t[0], "name": t[1], "operation": t[2], "destination": t[3], "Parameters": json.loads(t[4])}
                    for t in tasks
                ]).encode())

    def do_PUT(self):
        """Handle PUT requests to update a task."""
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
        """Handle DELETE requests to remove a task."""
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

# Start the server
PORT = 8000
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
