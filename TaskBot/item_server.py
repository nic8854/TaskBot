import http.server
import socketserver
import json
import sqlite3
from urllib.parse import urlparse, parse_qs

# Initialize SQLite Database
DATABASE_FILE = "items.db"

def init_db():
    """Initialize the SQLite database and create the items table if not exists."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT NOT NULL
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

    def fetch_items(self, item_name=None):
        """Fetch items from the database."""
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            if item_name:
                cursor.execute("SELECT * FROM items WHERE name = ?", (item_name,))
                return cursor.fetchone()
            else:
                cursor.execute("SELECT * FROM items")
                return cursor.fetchall()

    def add_item(self, item_data):
        """Add a item to the database."""
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                INSERT INTO items (name, description)
                VALUES (?, ?)
                """, (item_data["name"], item_data["description"]))
                conn.commit()
                return True, None
            except sqlite3.IntegrityError as e:
                return False, str(e)

    def update_item(self, item_name, item_data):
        """Update an existing item in the database."""
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE items
            SET operation = ?, destination = ?, parameters = ?
            WHERE name = ?
            """, (item_data["operation"], item_data["destination"], json.dumps(item_data["Parameters"]), item_name))
            conn.commit()
            return cursor.rowcount > 0

    def delete_item(self, item_name):
        """Delete a item from the database."""
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM items WHERE name = ?", (item_name,))
            conn.commit()
            return cursor.rowcount > 0

    def do_POST(self):
        """Handle POST requests to add a new item."""
        if self.path == '/items':
            try:
                item_data = json.loads(self._read_content())
                success, error = self.add_item(item_data)
                if success:
                    self._set_headers(201)
                    self.wfile.write(json.dumps({"message": "item added"}).encode())
                else:
                    self._set_headers(409)
                    self.wfile.write(json.dumps({"error": error}).encode())
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid data", "details": str(e)}).encode())

    def do_GET(self):
        """Handle GET requests to retrieve items."""
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        if parsed_path.path == '/items':
            item_name = query.get('name', [None])[0]
            if item_name:
                item = self.fetch_items(item_name)
                if item:
                    self._set_headers(200)
                    self.wfile.write(json.dumps({
                        "id": item[0], "name": item[1], "description": item[2]
                    }).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "item not found"}).encode())
            else:
                items = self.fetch_items()
                self._set_headers(200)
                self.wfile.write(json.dumps([
                    {"id": t[0], "name": t[1], "description": t[2]}
                    for t in items
                ]).encode())

    def do_PUT(self):
        """Handle PUT requests to update a item."""
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        if parsed_path.path == '/items':
            item_name = query.get('name', [None])[0]
            if item_name:
                item_data = json.loads(self._read_content())
                success = self.update_item(item_name, item_data)
                if success:
                    self._set_headers(200)
                    self.wfile.write(json.dumps({"message": "item updated"}).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "item not found"}).encode())

    def do_DELETE(self):
        """Handle DELETE requests to remove a item."""
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        if parsed_path.path == '/items':
            item_name = query.get('name', [None])[0]
            if item_name:
                success = self.delete_item(item_name)
                if success:
                    self._set_headers(200)
                    self.wfile.write(json.dumps({"message": "item deleted"}).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "item not found"}).encode())

# Initialize the database
init_db()

# Start the server
PORT = 8001
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Item Server serving at port {PORT}")
    httpd.serve_forever()
