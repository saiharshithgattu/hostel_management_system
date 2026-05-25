import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hostel.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('Admin', 'Warden', 'Student')),
        full_name TEXT NOT NULL,
        email TEXT,
        phone TEXT
    );
    """)

    # 2. Rooms Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_number TEXT UNIQUE NOT NULL,
        block TEXT NOT NULL,
        capacity INTEGER NOT NULL CHECK(capacity > 0),
        current_occupancy INTEGER DEFAULT 0 CHECK(current_occupancy >= 0),
        monthly_rent REAL NOT NULL CHECK(monthly_rent >= 0)
    );
    """)

    # 3. Students Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id INTEGER PRIMARY KEY,
        roll_number TEXT UNIQUE NOT NULL,
        branch TEXT,
        room_id INTEGER,
        admission_date TEXT,
        parent_name TEXT,
        parent_phone TEXT,
        FOREIGN KEY (student_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (room_id) REFERENCES rooms (id) ON DELETE SET NULL
    );
    """)

    # 4. Fees Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        amount_total REAL NOT NULL,
        amount_paid REAL DEFAULT 0.0,
        amount_due REAL NOT NULL,
        billing_period TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('Paid', 'Partially Paid', 'Unpaid')),
        due_date TEXT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE
    );
    """)

    # 5. Feedback / Complaints Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        subject TEXT NOT NULL,
        message TEXT NOT NULL,
        status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending', 'Reviewed', 'Resolved')),
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        admin_response TEXT,
        FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE
    );
    """)

    # 6. Visitors Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS visitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        visitor_name TEXT NOT NULL,
        relationship TEXT NOT NULL,
        contact TEXT NOT NULL,
        check_in TEXT DEFAULT CURRENT_TIMESTAMP,
        check_out TEXT,
        FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE
    );
    """)

    # 7. Notifications Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        target_role TEXT DEFAULT 'All' CHECK(target_role IN ('All', 'Student', 'Warden')),
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()

def query_db(query, args=(), one=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def modify_db(query, args=()):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, args)
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
