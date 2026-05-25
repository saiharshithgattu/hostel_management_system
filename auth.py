import hashlib
from db import query_db, modify_db, get_db_connection

def hash_password(password):
    """Simple SHA256 hashing for password safety without external dependencies."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(stored_hash, password):
    return stored_hash == hash_password(password)

def login_user(username, password):
    """
    Validates credentials and returns a user dictionary if success, else None.
    """
    user = query_db("SELECT * FROM users WHERE username = ?", (username,), one=True)
    if user and verify_password(user['password_hash'], password):
        return {
            'id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'full_name': user['full_name'],
            'email': user['email'],
            'phone': user['phone']
        }
    return None

def register_user(username, password, role, full_name, email="", phone=""):
    """
    Registers a generic user (e.g., Admin, Warden).
    """
    pwd_hash = hash_password(password)
    try:
        user_id = modify_db(
            "INSERT INTO users (username, password_hash, role, full_name, email, phone) VALUES (?, ?, ?, ?, ?, ?)",
            (username, pwd_hash, role, full_name, email, phone)
        )
        return user_id
    except Exception as e:
        print(f"Error registering user: {e}")
        return None

def register_student(username, password, full_name, email, phone, roll_number, branch, room_id=None, parent_name="", parent_phone=""):
    """
    Registers a student user, along with student-specific profile record and updates room occupancy if needed.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    pwd_hash = hash_password(password)
    try:
        # Check if roll number or username is already taken
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return False, "Username already exists."
        
        cursor.execute("SELECT student_id FROM students WHERE roll_number = ?", (roll_number,))
        if cursor.fetchone():
            return False, "Roll number already registered."
            
        # If room_id is specified, check room capacity
        if room_id:
            cursor.execute("SELECT capacity, current_occupancy FROM rooms WHERE id = ?", (room_id,))
            room = cursor.fetchone()
            if not room:
                return False, "Selected room does not exist."
            if room['current_occupancy'] >= room['capacity']:
                return False, "Selected room is already at full capacity."
                
        # Insert user
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, full_name, email, phone) VALUES (?, ?, 'Student', ?, ?, ?)",
            (username, pwd_hash, full_name, email, phone)
        )
        user_id = cursor.lastrowid
        
        # Insert student record
        import datetime
        adm_date = datetime.date.today().strftime("%Y-%m-%d")
        cursor.execute(
            "INSERT INTO students (student_id, roll_number, branch, room_id, admission_date, parent_name, parent_phone) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, roll_number, branch, room_id, adm_date, parent_name, parent_phone)
        )
        
        # Update room occupancy
        if room_id:
            cursor.execute("UPDATE rooms SET current_occupancy = current_occupancy + 1 WHERE id = ?", (room_id,))
            
        conn.commit()
        return True, "Student registered successfully."
    except Exception as e:
        conn.rollback()
        print(f"Error during transaction: {e}")
        return False, str(e)
    finally:
        conn.close()
