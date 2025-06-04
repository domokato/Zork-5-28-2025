import os
import sqlite3
import json

# --- Configuration ---
DB_PATH = os.path.join(os.path.dirname(__file__), "zork_world.db")

# --- Database Initialization ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Rooms table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS rooms (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        items TEXT
    )
    ''')

    # Directional connections table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS connections (
        from_room TEXT,
        to_room TEXT,
        direction TEXT,
        PRIMARY KEY (from_room, direction),
        FOREIGN KEY (from_room) REFERENCES rooms(id),
        FOREIGN KEY (to_room) REFERENCES rooms(id)
    )
    ''')

    conn.commit()
    conn.close()

# --- Room and Connection Utilities ---
def add_room(id, name, description, items=None):
    if items is None:
        items = []
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        'INSERT OR REPLACE INTO rooms (id, name, description, items) VALUES (?, ?, ?, ?)',
        (id, name, description, json.dumps(items))
    )
    conn.commit()
    conn.close()

def connect_rooms(from_room, to_room, direction):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        'INSERT OR REPLACE INTO connections (from_room, to_room, direction) VALUES (?, ?, ?)',
        (from_room, to_room, direction)
    )
    conn.commit()
    conn.close()

def get_room(room_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT id, name, description, items FROM rooms WHERE id = ?', (room_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "name": row[1],
        "description": row[2],
        "items": json.loads(row[3]) if row[3] else []
    }

def get_exits(room_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT direction, to_room FROM connections WHERE from_room = ?', (room_id,))
    exits = {row[0]: row[1] for row in cur.fetchall()}
    conn.close()
    return exits

# --- Grid World Generation ---
def create_grid_world(size=3):
    init_db()
    # Add rooms
    for y in range(size):
        for x in range(size):
            room_id = f"room_{y}_{x}"
            name = f"Room ({y},{x})"
            desc = f"You are in a square room located at coordinates ({y},{x})."
            add_room(room_id, name, desc, items=["stone"] if (x + y) % 2 == 0 else [])

    # Connect rooms with directions
    for y in range(size):
        for x in range(size):
            current = f"room_{y}_{x}"
            if y > 0:
                connect_rooms(current, f"room_{y-1}_{x}", "north")
            if y < size - 1:
                connect_rooms(current, f"room_{y+1}_{x}", "south")
            if x > 0:
                connect_rooms(current, f"room_{y}_{x-1}", "west")
            if x < size - 1:
                connect_rooms(current, f"room_{y}_{x+1}", "east")

# --- Example Use ---
if __name__ == "__main__":
    create_grid_world(size=3)

    # Example output
    room = get_room("room_1_1")
    exits = get_exits("room_1_1")

    print("\n--- Room Info ---")
    print(f"ID: {room['id']}")
    print(f"Name: {room['name']}")
    print(f"Description: {room['description']}")
    print(f"Items: {room['items']}")

    print("\n--- Available Exits ---")
    for direction, dest in exits.items():
        print(f"{direction.capitalize()}: {dest}")
