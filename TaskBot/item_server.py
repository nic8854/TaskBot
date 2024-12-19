import http.server
import socketserver
import json
import sqlite3
from urllib.parse import urlparse, parse_qs
import time
from datetime import datetime, timedelta

# Initialize SQLite Database
DATABASE_FILE = "items.db"

def init_db():
    """Initialize the SQLite database and create the items table if not exists."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            payload TEXT
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

    def fetch_items(self, item_id=None):
        """Fetch items from the database."""
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            if item_id:
                cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
                return cursor.fetchone()
            else:
                cursor.execute("SELECT * FROM items")
                return cursor.fetchall()

    def add_item(self, item_data):
        """Add an item to the database."""
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            try:
                cursor.execute("""
                INSERT INTO items (timestamp, payload)
                VALUES (?, ?)
                """, (now, item_data["payload"]))
                conn.commit()
                return True, None
            except sqlite3.IntegrityError as e:
                return False, str(e)

    def update_item(self, item_id, item_data):
        """Update an existing item in the database."""
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute("""
            UPDATE items
            SET timestamp = ?, payload = ?
            WHERE id = ?
            """, (now, item_data["payload"], item_id))
            conn.commit()
            return cursor.rowcount > 0

    def delete_item(self, item_id):
        """Delete an item from the database."""
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
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
            item_id = query.get('id', [None])[0]
            if item_id:
                item = self.fetch_items(item_id)
                if item:
                    self._set_headers(200)
                    self.wfile.write(json.dumps({
                        "id": item[0], "timestamp": item[1], "payload": item[2]
                    }).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "item not found"}).encode())
            else:
                items = self.fetch_items()
                self._set_headers(200)
                self.wfile.write(json.dumps([
                    {"id": t[0], "timestamp": t[1], "payload": t[2]}
                    for t in items
                ]).encode())

    def do_PUT(self):
        """Handle PUT requests to update an item."""
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        if parsed_path.path == '/items':
            item_id = query.get('id', [None])[0]
            if item_id:
                item_data = json.loads(self._read_content())
                success = self.update_item(item_id, item_data)
                if success:
                    self._set_headers(200)
                    self.wfile.write(json.dumps({"message": "item updated"}).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "item not found"}).encode())

    def do_DELETE(self):
        """Handle DELETE requests to remove an item."""
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)
        if parsed_path.path == '/items':
            item_id = query.get('id', [None])[0]
            if item_id:
                success = self.delete_item(item_id)
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
