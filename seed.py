import os
import datetime
from db import init_db, modify_db, get_db_connection
from auth import hash_password

def seed_database():
    print("Starting database seeding...")
    
    # 1. Initialize tables first
    init_db()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if database is already seeded
    cursor.execute("SELECT count(*) as count FROM users")
    if cursor.fetchone()['count'] > 0:
        print("Database already contains records. Skipping seed.")
        conn.close()
        return

    try:
        # 2. Add Users (Admin, Warden, and Students)
        print("Seeding Users...")
        # Admin
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, full_name, email, phone) VALUES (?, ?, ?, ?, ?, ?)",
            ("naven", hash_password("naveen@123"), "Admin", "Naveen Chief Administrator", "admin@hostel.com", "+1-800-555-0199")
        )
        admin_id = cursor.lastrowid
        
        # Warden
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, full_name, email, phone) VALUES (?, ?, ?, ?, ?, ?)",
            ("warden", hash_password("warden123"), "Warden", "Sarah Jenkins", "sarah.jenkins@hostel.com", "+1-800-555-0122")
        )
        warden_id = cursor.lastrowid
        
        # Students
        students_raw = [
            ("aditya", "aditya@123", "Aditya", "aditya@student.com", "9876543201", "2026CSE001", "Computer Science", "Ramesh Kumar", "9876543211"),
            ("harshith", "harshith@123", "Harshith", "harshith@student.com", "9876543202", "2026CSE002", "Computer Science", "Suresh Sharma", "9876543212"),
            ("chandu", "chandu@123", "Chandu", "chandu@student.com", "9876543203", "2026ECE001", "Electronics", "Vijay Patel", "9876543213"),
            ("goverdhan", "goverdhan@123", "Goverdhan", "goverdhan@student.com", "9876543204", "2026ME001", "Mechanical", "Anil Verma", "9876543214")
        ]
        
        students_ids = []
        for uname, pwd, name, email, phone, roll, branch, parent, parent_p in students_raw:
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, full_name, email, phone) VALUES (?, ?, ?, ?, ?, ?)",
                (uname, hash_password(pwd), "Student", name, email, phone)
            )
            uid = cursor.lastrowid
            students_ids.append((uid, roll, branch, parent, parent_p))

        # 3. Add Rooms
        print("Seeding Rooms...")
        rooms_raw = [
            ("101", "A", 2, 5000.0),
            ("102", "A", 2, 5000.0),
            ("103", "A", 2, 5000.0),
            ("201", "B", 3, 4500.0),
            ("202", "B", 3, 4500.0),
            ("301", "C", 1, 6000.0),
            ("302", "C", 1, 6000.0)
        ]
        
        room_map = {}
        for num, block, cap, rent in rooms_raw:
            cursor.execute(
                "INSERT INTO rooms (room_number, block, capacity, monthly_rent) VALUES (?, ?, ?, ?)",
                (num, block, cap, rent)
            )
            room_map[num] = cursor.lastrowid
            
        # 4. Allocate Students to Rooms and Update Occupancies
        print("Allocating Students...")
        allocations = [
            (students_ids[0], room_map["101"]), # Naveen -> 101
            (students_ids[1], room_map["101"]), # Aditya -> 101 (Room 101 is now full!)
            (students_ids[2], room_map["201"]), # Priya -> 201
            (students_ids[3], room_map["301"])  # Rahul -> 301
        ]
        
        today = datetime.date.today().strftime("%Y-%m-%d")
        
        for student_info, rid in allocations:
            uid, roll, branch, parent, parent_p = student_info
            cursor.execute(
                "INSERT INTO students (student_id, roll_number, branch, room_id, admission_date, parent_name, parent_phone) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (uid, roll, branch, rid, today, parent, parent_p)
            )
            # Update room occupancy
            cursor.execute("UPDATE rooms SET current_occupancy = current_occupancy + 1 WHERE id = ?", (rid,))

        # 5. Add Fees Billing Logs
        print("Seeding Fees...")
        fees_raw = [
            # Aditya
            (students_ids[0][0], 5000.0, 5000.0, 0.0, "May 2026", "Paid", "2026-05-10"),
            (students_ids[0][0], 5000.0, 0.0, 5000.0, "June 2026", "Unpaid", "2026-06-10"),
            # Harshith
            (students_ids[1][0], 5000.0, 2000.0, 3000.0, "May 2026", "Partially Paid", "2026-05-10"),
            # Chandu
            (students_ids[2][0], 4500.0, 0.0, 4500.0, "May 2026", "Unpaid", "2026-05-05"),
            # Goverdhan
            (students_ids[3][0], 6000.0, 6000.0, 0.0, "May 2026", "Paid", "2026-05-10")
        ]
        
        for uid, total, paid, due, period, status, due_d in fees_raw:
            cursor.execute(
                "INSERT INTO fees (student_id, amount_total, amount_paid, amount_due, billing_period, status, due_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (uid, total, paid, due, period, status, due_d)
            )

        # 6. Add Feedback
        print("Seeding Feedback...")
        cursor.execute(
            """INSERT INTO feedback (student_id, category, subject, message, status, admin_response, created_at) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (students_ids[0][0], "Maintenance", "Wi-Fi Issue in Block A", 
             "Wi-Fi in Block A is down since yesterday evening. The router shows no light. Please fix it ASAP.", 
             "Resolved", "The warden checked the power adapter and replaced it. The internet is now working.", 
             "2026-05-18 10:15:30")
        )
        cursor.execute(
            """INSERT INTO feedback (student_id, category, subject, message, status, created_at) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (students_ids[1][0], "Food", "Quality of Dinner Mess Food", 
             "The quality of rice and dal served during dinner has degraded. It's often watery and lacks taste.", 
             "Pending", "2026-05-19 08:30:10")
        )

        # 7. Add Notifications
        print("Seeding Notifications...")
        cursor.execute(
            "INSERT INTO notifications (title, message, target_role, created_at) VALUES (?, ?, ?, ?)",
            ("Annual Sports Meet 2026", "The Annual Hostel Sports registration is now open! Events include Football, Badminton, and Chess. Sign up at the Warden's desk before May 25.", "All", "2026-05-15 09:00:00")
        )
        cursor.execute(
            "INSERT INTO notifications (title, message, target_role, created_at) VALUES (?, ?, ?, ?)",
            ("Block B Power Outage Notice", "Please note that there will be a scheduled power maintenance outage in Block B on Thursday, May 21st, from 2:00 PM to 4:00 PM.", "Student", "2026-05-19 11:00:00")
        )
        cursor.execute(
            "INSERT INTO notifications (title, message, target_role, created_at) VALUES (?, ?, ?, ?)",
            ("Warden Review Meeting", "All wardens are requested to attend the monthly review meeting with the Admin today at 4:30 PM in Conference Room A.", "Warden", "2026-05-19 12:00:00")
        )

        # 8. Add Visitor Logs
        print("Seeding Visitor Logs...")
        cursor.execute(
            "INSERT INTO visitors (student_id, visitor_name, relationship, contact, check_in, check_out) VALUES (?, ?, ?, ?, ?, ?)",
            (students_ids[0][0], "Rajesh Kumar", "Father", "9876543255", "2026-05-18 09:30:00", "2026-05-18 13:00:00")
        )
        cursor.execute(
            "INSERT INTO visitors (student_id, visitor_name, relationship, contact, check_in) VALUES (?, ?, ?, ?, ?)",
            (students_ids[2][0], "Sunita Patel", "Mother", "9876543266", "2026-05-19 11:15:00")
        )

        conn.commit()
        print("Database successfully seeded with elegant mock records!")
    except Exception as e:
        conn.rollback()
        print(f"Error during seeding database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    seed_database()
