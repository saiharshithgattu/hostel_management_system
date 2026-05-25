import tkinter as tk
from tkinter import messagebox, ttk
import datetime
from theme import *
from db import query_db, modify_db, get_db_connection
from auth import register_student, hash_password

class AdminDashboard(tk.Frame):
    def __init__(self, parent, user, on_logout):
        super().__init__(parent, bg=BG_COLOR)
        self.user = user
        self.on_logout = on_logout
        
        # Sidebar Navigation
        self.sidebar = tk.Frame(self, bg=NAV_BG, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Sidebar Header (Logo/Title)
        lbl_logo = tk.Label(
            self.sidebar, 
            text="ADMIN PANEL", 
            bg=NAV_BG, 
            fg=ACCENT_COLOR, 
            font=FONT_SUBHEADING, 
            pady=20
        )
        lbl_logo.pack(fill="x")
        
        # Welcome label
        lbl_user = tk.Label(
            self.sidebar, 
            text=f"Welcome,\n{self.user['full_name']}", 
            bg=NAV_BG, 
            fg=TEXT_COLOR, 
            font=FONT_BODY_BOLD, 
            pady=10,
            wraplength=180
        )
        lbl_user.pack(fill="x", padx=10)
        
        # Nav Buttons list
        self.nav_buttons = {}
        self.tabs = ["Overview", "Students", "Rooms", "Fees", "Feedback", "Announcements"]
        
        for tab in self.tabs:
            btn = tk.Button(
                self.sidebar,
                text=f"  {tab}",
                anchor="w",
                bg=NAV_BG,
                fg=TEXT_MUTED,
                activebackground=CARD_BG,
                activeforeground=TEXT_COLOR,
                font=FONT_BODY_BOLD,
                relief="flat",
                bd=0,
                padx=15,
                pady=12,
                cursor="hand2",
                command=lambda t=tab: self.switch_tab(t)
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[tab] = btn
            
            # Hover bindings
            btn.bind("<Enter>", lambda e, b=btn: self.on_nav_enter(b))
            btn.bind("<Leave>", lambda e, b=btn: self.on_nav_leave(b))
            
        # Logout button
        btn_logout = tk.Button(
            self.sidebar,
            text="  Logout",
            anchor="w",
            bg=NAV_BG,
            fg=DANGER,
            activebackground=CARD_BG,
            activeforeground=DANGER,
            font=FONT_BODY_BOLD,
            relief="flat",
            bd=0,
            padx=15,
            pady=12,
            cursor="hand2",
            command=self.on_logout
        )
        btn_logout.pack(side="bottom", fill="x", pady=20)
        btn_logout.bind("<Enter>", lambda e, b=btn_logout: b.configure(bg="#2d1e24"))
        btn_logout.bind("<Leave>", lambda e, b=btn_logout: b.configure(bg=NAV_BG))

        # Main Content Frame
        self.content_container = tk.Frame(self, bg=BG_COLOR)
        self.content_container.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        # Active Tab Tracking
        self.active_tab = None
        self.switch_tab("Overview")
        
    def on_nav_enter(self, btn):
        if btn.cget("text").strip() != self.active_tab:
            btn.configure(bg=CARD_BG, fg=TEXT_COLOR)
            
    def on_nav_leave(self, btn):
        if btn.cget("text").strip() != self.active_tab:
            btn.configure(bg=NAV_BG, fg=TEXT_MUTED)
            
    def switch_tab(self, tab_name):
        if self.active_tab == tab_name:
            return
            
        self.active_tab = tab_name
        
        # Update Nav Styles
        for name, btn in self.nav_buttons.items():
            if name == tab_name:
                btn.configure(bg=ACCENT_COLOR, fg=TEXT_COLOR)
            else:
                btn.configure(bg=NAV_BG, fg=TEXT_MUTED)
                
        # Clear main content
        for child in self.content_container.winfo_children():
            child.destroy()
            
        # Render appropriate screen
        if tab_name == "Overview":
            self.render_overview()
        elif tab_name == "Students":
            self.render_students()
        elif tab_name == "Rooms":
            self.render_rooms()
        elif tab_name == "Fees":
            self.render_fees()
        elif tab_name == "Feedback":
            self.render_feedback()
        elif tab_name == "Announcements":
            self.render_announcements()

    # ==================== OVERVIEW SCREEN ====================
    def render_overview(self):
        lbl_head = tk.Label(self.content_container, text="Administrative Dashboard Overview", font=FONT_HEADING, bg=BG_COLOR, fg=TEXT_COLOR)
        lbl_head.pack(anchor="w", pady=(0, 20))
        
        # Calculate dynamic administration statistics
        tot_students = query_db("SELECT count(*) as count FROM students", one=True)['count']
        tot_rooms = query_db("SELECT count(*) as count FROM rooms", one=True)['count']
        total_revenue = query_db("SELECT SUM(amount_paid) as rev FROM fees", one=True)['rev'] or 0.0
        total_dues = query_db("SELECT SUM(amount_due) as dues FROM fees", one=True)['dues'] or 0.0
        
        stats_frame = tk.Frame(self.content_container, bg=BG_COLOR)
        stats_frame.pack(fill="x", pady=(0, 20))
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)
        stats_frame.grid_columnconfigure(3, weight=1)
        
        stats = [
            ("Total Students Enrolled", str(tot_students), ACCENT_COLOR, 0),
            ("Rooms Configured", str(tot_rooms), LIGHT_ACCENT, 1),
            ("Total Revenue Collected", f"₹{total_revenue:.2f}", SUCCESS, 2),
            ("Outstanding Due Fees", f"₹{total_dues:.2f}", DANGER, 3),
        ]
        
        for title, val, color, col in stats:
            card = StyledCard(stats_frame)
            card.grid(row=0, column=col, padx=4, sticky="ew")
            tk.Label(card, text=title, font=FONT_CAPTION, bg=CARD_BG, fg=TEXT_MUTED).pack(anchor="center")
            tk.Label(card, text=val, font=FONT_HEADING, bg=CARD_BG, fg=color).pack(anchor="center")
            
        # Split layout: Unresolved complaints on Left, Recent visitor movements on Right
        split_frame = tk.Frame(self.content_container, bg=BG_COLOR)
        split_frame.pack(fill="both", expand=True)
        split_frame.grid_columnconfigure(0, weight=1)
        split_frame.grid_columnconfigure(1, weight=1)
        
        # Left Side - Unresolved feedback
        card_fb = StyledCard(split_frame)
        card_fb.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        tk.Label(card_fb, text="Pending Complaints", font=FONT_SUBHEADING, bg=CARD_BG, fg=WARNING).pack(anchor="w", pady=(0, 10))
        
        fb_scroll = ScrollableFrame(card_fb)
        fb_scroll.pack(fill="both", expand=True)
        
        pending_fbs = query_db(
            """SELECT f.*, u.full_name 
               FROM feedback f 
               JOIN users u ON f.student_id = u.id 
               WHERE f.status = 'Pending' 
               ORDER BY f.created_at DESC"""
        )
        
        if not pending_fbs:
            tk.Label(fb_scroll.scrollable_frame, text="All student complaints are fully resolved!", font=FONT_BODY, bg=BG_COLOR, fg=SUCCESS).pack(pady=30)
        else:
            for pf in pending_fbs:
                pbox = tk.Frame(fb_scroll.scrollable_frame, bg=BG_COLOR, highlightbackground=BORDER_COLOR, highlightthickness=1, pady=8, padx=10)
                pbox.pack(fill="x", pady=4)
                
                tk.Label(pbox, text=f"{pf['full_name']} - {pf['subject']}", font=FONT_BODY_BOLD, bg=BG_COLOR, fg=TEXT_COLOR, anchor="w").pack(fill="x")
                tk.Label(pbox, text=pf['message'], font=FONT_BODY, bg=BG_COLOR, fg=TEXT_MUTED, anchor="w", wraplength=300, justify="left").pack(fill="x", pady=(2, 5))
                
                def open_resp_fast(f_id=pf['id']):
                    self.switch_tab("Feedback")
                    
                StyledButton(pbox, text="Resolve Now", command=open_resp_fast, variant="primary", font=FONT_CAPTION).pack(anchor="e")
                
        # Right Side - Checked-in visitors Roster
        card_v = StyledCard(split_frame)
        card_v.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        tk.Label(card_v, text="Hostel Visitor Registry (Active)", font=FONT_SUBHEADING, bg=CARD_BG, fg=ACCENT_COLOR).pack(anchor="w", pady=(0, 10))
        
        v_scroll = ScrollableFrame(card_v)
        v_scroll.pack(fill="both", expand=True)
        
        active_visitors = query_db(
            """SELECT v.*, u.full_name as student_name, r.room_number 
               FROM visitors v 
               JOIN students s ON v.student_id = s.student_id 
               JOIN users u ON s.student_id = u.id 
               LEFT JOIN rooms r ON s.room_id = r.id 
               WHERE v.check_out IS NULL 
               ORDER BY v.check_in DESC"""
        )
        
        if not active_visitors:
            tk.Label(v_scroll.scrollable_frame, text="No visitors currently checked-in.", font=FONT_BODY, bg=BG_COLOR, fg=TEXT_MUTED).pack(pady=30)
        else:
            for av in active_visitors:
                vbox = tk.Frame(v_scroll.scrollable_frame, bg=BG_COLOR, highlightbackground=BORDER_COLOR, highlightthickness=1, pady=8, padx=10)
                vbox.pack(fill="x", pady=4)
                
                tk.Label(vbox, text=f"{av['visitor_name']} ({av['relationship']})", font=FONT_BODY_BOLD, bg=BG_COLOR, fg=TEXT_COLOR, anchor="w").pack(fill="x")
                tk.Label(vbox, text=f"Visits Student: {av['student_name']} (Rm {av['room_number'] or 'N/A'})", font=FONT_BODY, bg=BG_COLOR, fg=TEXT_MUTED, anchor="w").pack(fill="x")
                tk.Label(vbox, text=f"Entered: {av['check_in']}", font=FONT_CAPTION, bg=BG_COLOR, fg=TEXT_MUTED, anchor="w").pack(fill="x")

    # ==================== STUDENTS MANAGEMENT ====================
    def render_students(self):
        lbl_head = tk.Label(self.content_container, text="Student Enrollment Manager", font=FONT_HEADING, bg=BG_COLOR, fg=TEXT_COLOR)
        lbl_head.pack(anchor="w", pady=(0, 15))
        
        action_frame = tk.Frame(self.content_container, bg=BG_COLOR)
        action_frame.pack(fill="x", pady=(0, 15))
        
        StyledButton(action_frame, text="+ Enroll New Student", command=self.open_enroll_modal, variant="success").pack(side="left", padx=(0, 15))
        
        tk.Label(action_frame, text="Search Directory:", font=FONT_BODY_BOLD, bg=BG_COLOR, fg=TEXT_MUTED).pack(side="left", padx=(10, 5))
        search_entry = StyledEntry(action_frame, placeholder="Name, Roll, Branch...", width=25)
        search_entry.pack(side="left", padx=(0, 10))
        
        cols = [("Name", 2), ("Roll Number", 2), ("Branch", 2), ("Room", 1), ("Admission Date", 2), ("Parent Contact", 2), ("Action", 1)]
        table = StyledTable(self.content_container, cols)
        table.pack(fill="both", expand=True)
        
        def load_students(query_str=""):
            table.clear()
            
            sql = """SELECT s.*, u.full_name, u.email, u.phone, u.username, r.room_number 
                     FROM students s 
                     JOIN users u ON s.student_id = u.id 
                     LEFT JOIN rooms r ON s.room_id = r.id"""
            args = ()
            if query_str:
                sql += " WHERE u.full_name LIKE ? OR s.roll_number LIKE ? OR s.branch LIKE ? OR r.room_number LIKE ?"
                arg = f"%{query_str}%"
                args = (arg, arg, arg, arg)
                
            students = query_db(sql, args)
            
            if not students:
                tk.Label(table.scroll_frame.scrollable_frame, text="No student records found.", font=FONT_BODY, bg=BG_COLOR, fg=TEXT_MUTED).pack(pady=20)
            else:
                for s in students:
                    row_frame = table.add_row([
                        s['full_name'],
                        s['roll_number'],
                        s['branch'] or "N/A",
                        f"Rm {s['room_number'] or 'N/A'}",
                        s['admission_date'],
                        s['parent_phone'] or "N/A",
                        "  [Edit/Delete]"
                    ], data=s, on_click=self.on_student_row_click)
                    
                    lbl_action = row_frame.winfo_children()[6]
                    lbl_action.configure(fg=ACCENT_COLOR, font=FONT_BODY_BOLD)
                    
        search_entry.entry.bind("<KeyRelease>", lambda e: load_students(search_entry.get().strip()))
        load_students()
        
    def on_student_row_click(self, student):
        # Open detailed profile / actions sheet
        modal = tk.Toplevel(self)
        modal.title(f"Manage Student: {student['full_name']}")
        modal.geometry("380x420")
        modal.configure(bg=BG_COLOR)
        modal.transient(self)
        modal.grab_set()
        
        modal.update_idletasks()
        w = modal.winfo_width()
        h = modal.winfo_height()
        modal.geometry(f"+{int((self.winfo_screenwidth() - w) / 2)}+{int((self.winfo_screenheight() - h) / 2)}")
        
        tk.Label(modal, text=student['full_name'], font=FONT_SUBHEADING, bg=BG_COLOR, fg=ACCENT_COLOR, pady=15).pack()
        
        card = StyledCard(modal)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        details = [
            ("Roll No:", student['roll_number']),
            ("Branch:", student['branch']),
            ("Room Number:", f"Rm {student['room_number'] or 'N/A'}"),
            ("Email:", student['email'] or "N/A"),
            ("Phone:", student['phone'] or "N/A"),
            ("Parent Name:", student['parent_name'] or "N/A"),
            ("Parent Phone:", student['parent_phone'] or "N/A"),
        ]
        
        for k, v in details:
            r = tk.Frame(card, bg=CARD_BG, pady=2)
            r.pack(fill="x")
            tk.Label(r, text=k, font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_MUTED, width=15, anchor="w").pack(side="left")
            tk.Label(r, text=v, font=FONT_BODY, bg=CARD_BG, fg=TEXT_COLOR).pack(side="left")
            
        def delete_stud():
            ans = messagebox.askyesno("Confirm Delete", f"Are you sure you want to permanently delete student {student['full_name']}?\nThis action will also free up room occupancy.", parent=modal)
            if ans:
                # Decrement room occupancy
                if student['room_id']:
                    modify_db("UPDATE rooms SET current_occupancy = current_occupancy - 1 WHERE id = ?", (student['room_id'],))
                    
                # Cascade deletion (handled by SQLite triggers / manual code since users is parent)
                modify_db("DELETE FROM users WHERE id = ?", (student['student_id'],))
                
                modal.destroy()
                messagebox.showinfo("Deleted", "Student profile has been permanently removed.")
                self.render_students()
                
        StyledButton(card, text="Delete Student Record", command=delete_stud, variant="danger").pack(fill="x", pady=(15, 0))
        StyledButton(card, text="Close Details", command=modal.destroy, variant="secondary").pack(fill="x", pady=(8, 0))

    def open_enroll_modal(self):
        modal = tk.Toplevel(self)
        modal.title("Register Student Profile")
        modal.geometry("450x640")
        modal.configure(bg=BG_COLOR)
        modal.transient(self)
        modal.grab_set()
        
        modal.update_idletasks()
        w = modal.winfo_width()
        h = modal.winfo_height()
        modal.geometry(f"+{int((self.winfo_screenwidth() - w) / 2)}+{int((self.winfo_screenheight() - h) / 2)}")
        
        tk.Label(modal, text="New Student Registration", font=FONT_SUBHEADING, bg=BG_COLOR, fg=ACCENT_COLOR, pady=15).pack()
        
        # Scrollable form container
        form_scroll = ScrollableFrame(modal)
        form_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        card = StyledCard(form_scroll.scrollable_frame)
        card.pack(fill="both", expand=True, pady=5)
        
        # Form inputs
        inputs = {}
        fields = [
            ("username", "System Username", "Choose a unique username", False),
            ("password", "Login Password", "Min 6 characters", True),
            ("full_name", "Student Full Name", "Enter student's full name", False),
            ("email", "Email Address", "student@domain.com", False),
            ("phone", "Contact Mobile", "10-digit number", False),
            ("roll_number", "University Roll Number", "e.g., 2026CSE005", False),
            ("branch", "Branch/Major Discipline", "e.g., Computer Science", False),
            ("parent_name", "Parent / Guardian Name", "Full name of parent", False),
            ("parent_phone", "Parent Emergency Contact", "Emergency contact phone", False)
        ]
        
        for key, label, place, is_pwd in fields:
            tk.Label(card, text=label, font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(8, 2))
            show_char = "*" if is_pwd else ""
            ent = StyledEntry(card, placeholder=place, show=show_char)
            ent.pack(fill="x")
            inputs[key] = ent
            
        # Rooms allocation select box
        tk.Label(card, text="Room Allotment (Available Beds)", font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(8, 2))
        rooms = query_db("SELECT * FROM rooms WHERE current_occupancy < capacity")
        room_opts = [f"Room {r['room_number']} (Block {r['block']}, Cap: {r['current_occupancy']}/{r['capacity']}, Rent: ₹{r['monthly_rent']:.0f})" for r in rooms]
        room_ids = {f"Room {r['room_number']} (Block {r['block']}, Cap: {r['current_occupancy']}/{r['capacity']}, Rent: ₹{r['monthly_rent']:.0f})": r['id'] for r in rooms}
        
        room_opts.insert(0, "Do Not Allocate Now (Keep Pending)")
        room_ids["Do Not Allocate Now (Keep Pending)"] = None
        
        sel_room_var = tk.StringVar(value=room_opts[0])
        opt_frame = tk.Frame(card, bg=BG_COLOR, highlightbackground=BORDER_COLOR, highlightthickness=1)
        opt_frame.pack(fill="x", pady=(0, 15))
        
        drop = ttk.Combobox(opt_frame, textvariable=sel_room_var, values=room_opts, state="readonly", font=FONT_BODY)
        drop.pack(fill="both", expand=True, padx=5, pady=5)
        
        def save_student():
            vals = {k: v.get().strip() for k, v in inputs.items()}
            
            # Simple validation
            if not vals['username'] or not vals['password'] or not vals['full_name'] or not vals['roll_number']:
                messagebox.showerror("Error", "Username, Password, Full Name, and Roll Number are mandatory.")
                return
                
            if len(vals['password']) < 4:
                messagebox.showerror("Error", "Password must be at least 4 characters long.")
                return
                
            selected_room_text = sel_room_var.get()
            allocated_room_id = room_ids[selected_room_text]
            
            # Call Registration Auth layer
            success, msg = register_student(
                username=vals['username'],
                password=vals['password'],
                full_name=vals['full_name'],
                email=vals['email'],
                phone=vals['phone'],
                roll_number=vals['roll_number'],
                branch=vals['branch'],
                room_id=allocated_room_id,
                parent_name=vals['parent_name'],
                parent_phone=vals['parent_phone']
            )
            
            if success:
                modal.destroy()
                messagebox.showinfo("Success", "New student record has been added to registry!")
                self.render_students()
            else:
                messagebox.showerror("Registration Error", msg)
                
        StyledButton(card, text="Confirm Registration", command=save_student, variant="success").pack(fill="x")

    # ==================== ROOMS & OCCUPANCY ====================
    def render_rooms(self):
        lbl_head = tk.Label(self.content_container, text="Room Allotment & Visual Capacity Map", font=FONT_HEADING, bg=BG_COLOR, fg=TEXT_COLOR)
        lbl_head.pack(anchor="w", pady=(0, 15))
        
        # Add Room and Quick Stats Bar
        action_frame = tk.Frame(self.content_container, bg=BG_COLOR)
        action_frame.pack(fill="x", pady=(0, 15))
        
        StyledButton(action_frame, text="+ Add New Room", command=self.open_add_room_modal, variant="primary").pack(side="left", padx=(0, 15))
        
        # Table listing of all rooms
        rooms = query_db("SELECT * FROM rooms ORDER BY block ASC, room_number ASC")
        
        cols = [("Room No", 1), ("Block", 1), ("Capacity", 2), ("Beds Allocated", 2), ("Beds Available", 2), ("Monthly Rent", 2), ("Status Badge", 2)]
        table = StyledTable(self.content_container, cols)
        table.pack(fill="both", expand=True)
        
        for r in rooms:
            avail = r['capacity'] - r['current_occupancy']
            status = "Full" if avail == 0 else ("Available" if r['current_occupancy'] == 0 else "Partially Occupied")
            
            row_data = [
                f"Room {r['room_number']}",
                f"Block {r['block']}",
                str(r['capacity']),
                str(r['current_occupancy']),
                str(avail),
                f"₹{r['monthly_rent']:.2f}",
                status
            ]
            row_frame = table.add_row(row_data, data=r, on_click=self.on_room_row_click)
            
            # Format status badge column
            lbl_status = row_frame.winfo_children()[6]
            if status == "Full":
                lbl_status.configure(fg=DANGER, font=FONT_BODY_BOLD)
            elif status == "Available":
                lbl_status.configure(fg=SUCCESS, font=FONT_BODY_BOLD)
            else:
                lbl_status.configure(fg=WARNING, font=FONT_BODY_BOLD)

    def on_room_row_click(self, room):
        # Open visual details of who resides in selected room
        modal = tk.Toplevel(self)
        modal.title(f"Room Allocation details: Room {room['room_number']}")
        modal.geometry("380x360")
        modal.configure(bg=BG_COLOR)
        modal.transient(self)
        modal.grab_set()
        
        modal.update_idletasks()
        w = modal.winfo_width()
        h = modal.winfo_height()
        modal.geometry(f"+{int((self.winfo_screenwidth() - w) / 2)}+{int((self.winfo_screenheight() - h) / 2)}")
        
        tk.Label(modal, text=f"Room {room['room_number']} Residents", font=FONT_SUBHEADING, bg=BG_COLOR, fg=ACCENT_COLOR, pady=15).pack()
        
        card = StyledCard(modal)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Display general room capacity specs
        specs_frame = tk.Frame(card, bg=CARD_BG, pady=5)
        specs_frame.pack(fill="x")
        tk.Label(specs_frame, text=f"Block {room['block']} | Monthly Rent: ₹{room['monthly_rent']:.0f} | Capacity: {room['current_occupancy']}/{room['capacity']}", 
                 font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_MUTED).pack(anchor="center")
        
        # Query students occupying the room
        residents = query_db(
            """SELECT s.student_id, u.full_name, s.roll_number, s.branch 
               FROM students s 
               JOIN users u ON s.student_id = u.id 
               WHERE s.room_id = ?""",
            (room['id'],)
        )
        
        tk.Label(card, text="Assigned Residents:", font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(10, 5))
        
        if not residents:
            tk.Label(card, text="This room is currently empty.", font=FONT_BODY, bg=CARD_BG, fg=TEXT_MUTED).pack(pady=15)
        else:
            for res in residents:
                rbox = tk.Frame(card, bg=CARD_BG, highlightbackground=BORDER_COLOR, highlightthickness=1, pady=6, padx=8)
                rbox.pack(fill="x", pady=4)
                
                tk.Label(rbox, text=res['full_name'], font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(side="left")
                tk.Label(rbox, text=f"({res['roll_number']})", font=FONT_CAPTION, bg=CARD_BG, fg=TEXT_MUTED).pack(side="left", padx=5)
                
                def deallocate_student(s_id=res['student_id'], r_name=res['full_name']):
                    ans = messagebox.askyesno("Deallocate Student", f"Remove student {r_name} from Room {room['room_number']}?", parent=modal)
                    if ans:
                        modify_db("UPDATE students SET room_id = NULL WHERE student_id = ?", (s_id,))
                        modify_db("UPDATE rooms SET current_occupancy = current_occupancy - 1 WHERE id = ?", (room['id'],))
                        modal.destroy()
                        messagebox.showinfo("Success", "Student deallocated from room.")
                        self.render_rooms()
                        
                btn_remove = StyledButton(rbox, text="Deallocate", command=deallocate_student, variant="danger", font=FONT_CAPTION, padx=6, pady=2)
                btn_remove.pack(side="right")
                
        StyledButton(card, text="Close Details", command=modal.destroy, variant="secondary").pack(fill="x", pady=(15, 0))

    def open_add_room_modal(self):
        modal = tk.Toplevel(self)
        modal.title("Configure New Room")
        modal.geometry("360x360")
        modal.configure(bg=BG_COLOR)
        modal.transient(self)
        modal.grab_set()
        
        modal.update_idletasks()
        w = modal.winfo_width()
        h = modal.winfo_height()
        modal.geometry(f"+{int((self.winfo_screenwidth() - w) / 2)}+{int((self.winfo_screenheight() - h) / 2)}")
        
        tk.Label(modal, text="Add New Room", font=FONT_SUBHEADING, bg=BG_COLOR, fg=ACCENT_COLOR, pady=15).pack()
        
        card = StyledCard(modal)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        tk.Label(card, text="Room Number", font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 2))
        num_entry = StyledEntry(card, placeholder="e.g., 104")
        num_entry.pack(fill="x", pady=(0, 10))
        
        tk.Label(card, text="Hostel Block Designation", font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 2))
        block_entry = StyledEntry(card, placeholder="e.g., A")
        block_entry.pack(fill="x", pady=(0, 10))
        
        tk.Label(card, text="Beds Capacity", font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 2))
        cap_entry = StyledEntry(card, placeholder="e.g., 2")
        cap_entry.pack(fill="x", pady=(0, 10))
        
        tk.Label(card, text="Monthly Rental Fee (₹)", font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 2))
        rent_entry = StyledEntry(card, placeholder="e.g., 5000")
        rent_entry.pack(fill="x", pady=(0, 15))
        
        def save_room():
            num = num_entry.get().strip()
            blk = block_entry.get().strip().upper()
            cap_str = cap_entry.get().strip()
            rent_str = rent_entry.get().strip()
            
            if not num or not blk or not cap_str or not rent_str:
                messagebox.showerror("Error", "Please fill in all room specifications.")
                return
                
            try:
                cap = int(cap_str)
                rent = float(rent_str)
                if cap <= 0 or rent < 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Error", "Capacity must be positive integer and Rent must be non-negative numeric value.")
                return
                
            try:
                modify_db(
                    "INSERT INTO rooms (room_number, block, capacity, monthly_rent) VALUES (?, ?, ?, ?)",
                    (num, blk, cap, rent)
                )
                modal.destroy()
                messagebox.showinfo("Success", f"Room {num} registered successfully in Block {blk}!")
                self.render_rooms()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save room. Number might already exist: {e}")
                
        StyledButton(card, text="Register Room", command=save_room, variant="success").pack(fill="x")

    # ==================== FEES BILLING MANAGEMENT ====================
    def render_fees(self):
        lbl_head = tk.Label(self.content_container, text="Student Billing & Financial Audits", font=FONT_HEADING, bg=BG_COLOR, fg=TEXT_COLOR)
        lbl_head.pack(anchor="w", pady=(0, 15))
        
        action_frame = tk.Frame(self.content_container, bg=BG_COLOR)
        action_frame.pack(fill="x", pady=(0, 15))
        
        StyledButton(action_frame, text="+ Create Fee Invoice", command=self.open_issue_bill_modal, variant="primary").pack(side="left", padx=(0, 15))
        StyledButton(action_frame, text="Generate Monthly Room Bills", command=self.generate_bulk_monthly_bills, variant="warning").pack(side="left")
        
        # Display fees log
        fees_list = query_db(
            """SELECT f.*, u.full_name, s.roll_number 
               FROM fees f 
               JOIN students s ON f.student_id = s.student_id 
               JOIN users u ON s.student_id = u.id 
               ORDER BY f.due_date DESC"""
        )
        
        cols = [("Billing Period", 1), ("Student Name", 2), ("Roll Number", 2), ("Total Billed", 2), ("Amount Paid", 2), ("Outstanding Due", 2), ("Status", 1), ("Due Date", 2)]
        table = StyledTable(self.content_container, cols)
        table.pack(fill="both", expand=True)
        
        for f in fees_list:
            status = f['status']
            row_data = [
                f['billing_period'],
                f['full_name'],
                f['roll_number'],
                f"₹{f['amount_total']:.2f}",
                f"₹{f['amount_paid']:.2f}",
                f"₹{f['amount_due']:.2f}",
                status,
                f['due_date']
            ]
            row_frame = table.add_row(row_data, data=f, on_click=self.on_fee_row_click)
            
            # Color status text dynamically
            lbl_status = row_frame.winfo_children()[6]
            if status == "Paid":
                lbl_status.configure(fg=SUCCESS, font=FONT_BODY_BOLD)
            elif status == "Partially Paid":
                lbl_status.configure(fg=WARNING, font=FONT_BODY_BOLD)
            else:
                lbl_status.configure(fg=DANGER, font=FONT_BODY_BOLD)

    def on_fee_row_click(self, fee):
        if fee['status'] == "Paid":
            messagebox.showinfo("Bill Paid", f"Bill details for {fee['billing_period']} (Roll: {fee['roll_number']}) is fully completed.")
            return
            
        modal = tk.Toplevel(self)
        modal.title(f"Record Student Payment: {fee['full_name']}")
        modal.geometry("380x380")
        modal.configure(bg=BG_COLOR)
        modal.transient(self)
        modal.grab_set()
        
        modal.update_idletasks()
        w = modal.winfo_width()
        h = modal.winfo_height()
        modal.geometry(f"+{int((self.winfo_screenwidth() - w) / 2)}+{int((self.winfo_screenheight() - h) / 2)}")
        
        tk.Label(modal, text="Log Manual Cash/Card Payment", font=FONT_SUBHEADING, bg=BG_COLOR, fg=ACCENT_COLOR, pady=15).pack()
        
        card = StyledCard(modal)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        details = [
            ("Student Name:", fee['full_name']),
            ("Billing Period:", fee['billing_period']),
            ("Outstanding Due:", f"₹{fee['amount_due']:.2f}")
        ]
        for k, v in details:
            r = tk.Frame(card, bg=CARD_BG, pady=2)
            r.pack(fill="x")
            tk.Label(r, text=k, font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_MUTED, width=15, anchor="w").pack(side="left")
            tk.Label(r, text=v, font=FONT_BODY, bg=CARD_BG, fg=TEXT_COLOR).pack(side="left")
            
        tk.Label(card, text="Record Payment Amount Received (₹):", font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(15, 2))
        amount_entry = StyledEntry(card, placeholder=str(fee['amount_due']))
        amount_entry.pack(fill="x", pady=(0, 15))
        
        def save_payment():
            try:
                pay_amt = float(amount_entry.get())
                if pay_amt <= 0:
                    raise ValueError("Amount must be positive.")
                if pay_amt > fee['amount_due']:
                    raise ValueError("Cannot pay more than outstanding due.")
            except ValueError as ve:
                messagebox.showerror("Error", str(ve) or "Please enter valid payment number.")
                return
                
            new_paid = fee['amount_paid'] + pay_amt
            new_due = fee['amount_total'] - new_paid
            new_status = "Paid" if new_due == 0 else "Partially Paid"
            
            modify_db(
                "UPDATE fees SET amount_paid = ?, amount_due = ?, status = ? WHERE id = ?",
                (new_paid, new_due, new_status, fee['id'])
            )
            
            modal.destroy()
            messagebox.showinfo("Success", f"Recorded payment of ₹{pay_amt:.2f} successfully!")
            self.render_fees()
            
        StyledButton(card, text="Submit Payment Entry", command=save_payment, variant="success").pack(fill="x")

    def open_issue_bill_modal(self):
        modal = tk.Toplevel(self)
        modal.title("Issue Custom Fee Invoice")
        modal.geometry("380x420")
        modal.configure(bg=BG_COLOR)
        modal.transient(self)
        modal.grab_set()
        
        modal.update_idletasks()
        w = modal.winfo_width()
        h = modal.winfo_height()
        modal.geometry(f"+{int((self.winfo_screenwidth() - w) / 2)}+{int((self.winfo_screenheight() - h) / 2)}")
        
        tk.Label(modal, text="New Custom Invoice Details", font=FONT_SUBHEADING, bg=BG_COLOR, fg=ACCENT_COLOR, pady=15).pack()
        
        card = StyledCard(modal)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Student dropdown list
        students = query_db("SELECT s.student_id, u.full_name, s.roll_number FROM students s JOIN users u ON s.student_id = u.id")
        student_opts = [f"{s['full_name']} ({s['roll_number']})" for s in students]
        student_ids = {f"{s['full_name']} ({s['roll_number']})": s['student_id'] for s in students}
        
        tk.Label(card, text="Select Student Profile", font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 2))
        sel_stud_var = tk.StringVar()
        opt_frame = tk.Frame(card, bg=BG_COLOR, highlightbackground=BORDER_COLOR, highlightthickness=1)
        opt_frame.pack(fill="x", pady=(0, 10))
        drop = ttk.Combobox(opt_frame, textvariable=sel_stud_var, values=student_opts, state="readonly", font=FONT_BODY)
        drop.pack(fill="both", expand=True, padx=5, pady=5)
        if student_opts:
            drop.current(0)
            
        tk.Label(card, text="Billing Period Label", font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 2))
        period_entry = StyledEntry(card, placeholder="e.g., June 2026")
        period_entry.pack(fill="x", pady=(0, 10))
        
        tk.Label(card, text="Invoice Amount (₹)", font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 2))
        amt_entry = StyledEntry(card, placeholder="e.g., 2500")
        amt_entry.pack(fill="x", pady=(0, 10))
        
        tk.Label(card, text="Due Date (YYYY-MM-DD)", font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 2))
        due_d_entry = StyledEntry(card, placeholder=datetime.date.today().strftime("%Y-%m-%d"))
        due_d_entry.pack(fill="x", pady=(0, 15))
        
        def save_invoice():
            stud_sel = sel_stud_var.get()
            period = period_entry.get().strip()
            amt_str = amt_entry.get().strip()
            due_d = due_d_entry.get().strip()
            
            if not stud_sel or not period or not amt_str or not due_d:
                messagebox.showerror("Error", "Please fill in all invoice fields.")
                return
                
            try:
                amt = float(amt_str)
                if amt <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Error", "Please enter positive numeric billing amount.")
                return
                
            stud_id = student_ids[stud_sel]
            
            modify_db(
                "INSERT INTO fees (student_id, amount_total, amount_due, billing_period, status, due_date) VALUES (?, ?, ?, ?, 'Unpaid', ?)",
                (stud_id, amt, amt, period, due_d)
            )
            
            modal.destroy()
            messagebox.showinfo("Success", f"Custom billing invoice has been successfully assigned to student.")
            self.render_fees()
            
        StyledButton(card, text="Issue Invoice", command=save_invoice, variant="success").pack(fill="x")

    def generate_bulk_monthly_bills(self):
        # Automatically generate monthly room rent bill for every student who is allocated in a room!
        curr_month = datetime.date.today().strftime("%B %Y") # e.g., May 2026
        
        # Verify if bills for current month are already generated
        exists = query_db("SELECT count(*) as cnt FROM fees WHERE billing_period = ?", (curr_month,), one=True)['cnt']
        if exists > 0:
            ans = messagebox.askyesno("Bills Exist", f"Billing bills for {curr_month} already exist. Would you like to issue another cycle?")
            if not ans:
                return
                
        students_in_rooms = query_db(
            """SELECT s.student_id, r.monthly_rent 
               FROM students s 
               JOIN rooms r ON s.room_id = r.id"""
        )
        
        if not students_in_rooms:
            messagebox.showinfo("No Actions Needed", "No students are currently allocated to any room in the hostel.")
            return
            
        due_date = (datetime.date.today() + datetime.timedelta(days=10)).strftime("%Y-%m-%d")
        
        count = 0
        for sr in students_in_rooms:
            modify_db(
                "INSERT INTO fees (student_id, amount_total, amount_due, billing_period, status, due_date) VALUES (?, ?, ?, ?, 'Unpaid', ?)",
                (sr['student_id'], sr['monthly_rent'], sr['monthly_rent'], curr_month, due_date)
            )
            count += 1
            
        messagebox.showinfo("Success", f"Successfully generated {count} room rent billing invoices for {curr_month}!\nDue date set for: {due_date}")
        self.render_fees()

    # ==================== FEEDBACK & COMPLAINTS ====================
    def render_feedback(self):
        lbl_head = tk.Label(self.content_container, text="Feedback & Complaint Response Center", font=FONT_HEADING, bg=BG_COLOR, fg=TEXT_COLOR)
        lbl_head.pack(anchor="w", pady=(0, 20))
        
        # Split layout: Tickets list on Left, Response card editor on Right
        self.split_fb = tk.Frame(self.content_container, bg=BG_COLOR)
        self.split_fb.pack(fill="both", expand=True)
        self.split_fb.grid_columnconfigure(0, weight=2)
        self.split_fb.grid_columnconfigure(1, weight=3)
        
        # Left Panel - Scrollable Tickets roster
        card_list = StyledCard(self.split_fb)
        card_list.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        self.fb_tickets_scroll = ScrollableFrame(card_list)
        self.fb_tickets_scroll.pack(fill="both", expand=True)
        
        self.load_feedback_roster()
        
        # Right Panel - Empty placeholder
        self.resp_panel = StyledCard(self.split_fb)
        self.resp_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        tk.Label(self.resp_panel, text="Select a ticket from the left panel to compose administrative response and update resolution statuses.", 
                 font=FONT_BODY, bg=CARD_BG, fg=TEXT_MUTED, wraplength=350, justify="center").pack(fill="both", expand=True)

    def load_feedback_roster(self):
        # Clear scrollable frame children
        for c in self.fb_tickets_scroll.scrollable_frame.winfo_children():
            c.destroy()
            
        tickets = query_db(
            """SELECT f.*, u.full_name, s.roll_number, r.room_number 
               FROM feedback f 
               JOIN students s ON f.student_id = s.student_id 
               JOIN users u ON s.student_id = u.id 
               LEFT JOIN rooms r ON s.room_id = r.id 
               ORDER BY f.status DESC, f.created_at DESC"""
        )
        
        if not tickets:
            tk.Label(self.fb_tickets_scroll.scrollable_frame, text="No feedback tickets logged.", font=FONT_BODY, bg=BG_COLOR, fg=TEXT_MUTED).pack(pady=20)
        else:
            for t in tickets:
                status = t['status']
                bg_t = CARD_BG
                
                tbox = tk.Frame(self.fb_tickets_scroll.scrollable_frame, bg=bg_t, highlightbackground=BORDER_COLOR, highlightthickness=1, pady=8, padx=10)
                tbox.pack(fill="x", pady=4)
                
                # Header category and status color
                h = tk.Frame(tbox, bg=bg_t)
                h.pack(fill="x")
                tk.Label(h, text=f"[{t['category']}]", font=FONT_BODY_BOLD, bg=bg_t, fg=LIGHT_ACCENT).pack(side="left")
                
                s_color = SUCCESS if status == "Resolved" else (WARNING if status == "Reviewed" else TEXT_MUTED)
                tk.Label(h, text=status, font=FONT_BODY_BOLD, bg=bg_t, fg=s_color).pack(side="right")
                
                tk.Label(tbox, text=f"{t['full_name']} (Rm {t['room_number'] or 'N/A'})", font=FONT_BODY_BOLD, bg=bg_t, fg=TEXT_COLOR, anchor="w").pack(fill="x", pady=(2, 2))
                tk.Label(tbox, text=t['subject'], font=FONT_BODY, bg=bg_t, fg=TEXT_MUTED, anchor="w").pack(fill="x")
                
                # Bind click event
                for w in [tbox] + list(tbox.winfo_children()) + list(h.winfo_children()):
                    w.bind("<Button-1>", lambda e, tk_data=t: self.open_feedback_response_panel(tk_data))
                    w.configure(cursor="hand2")

    def open_feedback_response_panel(self, ticket):
        # Clear Right panel
        for child in self.resp_panel.winfo_children():
            child.destroy()
            
        tk.Label(self.resp_panel, text="Ticket Action Center", font=FONT_SUBHEADING, bg=CARD_BG, fg=ACCENT_COLOR).pack(anchor="w", pady=(0, 15))
        
        # Details grid
        details = [
            ("Logged Student:", ticket['full_name']),
            ("Roll Number:", ticket['roll_number']),
            ("Category:", ticket['category']),
            ("Subject:", ticket['subject']),
            ("Details:", ticket['message']),
            ("Logged Date:", ticket['created_at'])
        ]
        
        for k, v in details:
            r = tk.Frame(self.resp_panel, bg=CARD_BG, pady=3)
            r.pack(fill="x")
            tk.Label(r, text=k, font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_MUTED, width=15, anchor="w").pack(side="left")
            tk.Label(r, text=v, font=FONT_BODY, bg=CARD_BG, fg=TEXT_COLOR, justify="left", wraplength=280).pack(side="left")
            
        divider = tk.Frame(self.resp_panel, height=1, bg=BORDER_COLOR)
        divider.pack(fill="x", pady=10)
        
        tk.Label(self.resp_panel, text="Administrative Remarks / Response Message", font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 2))
        
        resp_frame = tk.Frame(self.resp_panel, bg=BG_COLOR, highlightbackground=BORDER_COLOR, highlightthickness=1)
        resp_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        resp_text = tk.Text(resp_frame, bg=BG_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, 
                            relief="flat", font=FONT_BODY, bd=0, height=4, wrap="word")
        resp_text.pack(fill="both", expand=True, padx=8, pady=8)
        
        if ticket['admin_response']:
            resp_text.insert("1.0", ticket['admin_response'])
            
        # Status update actions
        btn_frame = tk.Frame(self.resp_panel, bg=CARD_BG)
        btn_frame.pack(fill="x")
        
        def update_status(new_status):
            remark = resp_text.get("1.0", tk.END).strip()
            if not remark:
                messagebox.showerror("Error", "Please write response comment first.")
                return
                
            modify_db(
                "UPDATE feedback SET admin_response = ?, status = ? WHERE id = ?",
                (remark, new_status, ticket['id'])
            )
            
            messagebox.showinfo("Success", f"Ticket has been successfully updated to status: {new_status}!")
            self.render_feedback() # Refresh the tab
            
        StyledButton(btn_frame, text="Resolve Complaint", command=lambda: update_status("Resolved"), variant="success").pack(side="right", padx=2)
        StyledButton(btn_frame, text="Mark Reviewed", command=lambda: update_status("Reviewed"), variant="primary").pack(side="right", padx=2)

    # ==================== ANNOUNCEMENTS / NOTICES ====================
    def render_announcements(self):
        lbl_head = tk.Label(self.content_container, text="Announcements Noticeboard Manager", font=FONT_HEADING, bg=BG_COLOR, fg=TEXT_COLOR)
        lbl_head.pack(anchor="w", pady=(0, 20))
        
        split = tk.Frame(self.content_container, bg=BG_COLOR)
        split.pack(fill="both", expand=True)
        split.grid_columnconfigure(0, weight=2)
        split.grid_columnconfigure(1, weight=3)
        
        # Left Frame - Post Announcement
        card_form = StyledCard(split)
        card_form.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        tk.Label(card_form, text="Publish New Notification", font=FONT_SUBHEADING, bg=CARD_BG, fg=ACCENT_COLOR).pack(anchor="w", pady=(0, 15))
        
        tk.Label(card_form, text="Title", font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 2))
        title_entry = StyledEntry(card_form, placeholder="Notification Subject Title")
        title_entry.pack(fill="x", pady=(0, 10))
        
        tk.Label(card_form, text="Target Audience Group", font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 2))
        audiences = ["All", "Student", "Warden"]
        aud_var = tk.StringVar(value=audiences[0])
        opt_frame = tk.Frame(card_form, bg=BG_COLOR, highlightbackground=BORDER_COLOR, highlightthickness=1)
        opt_frame.pack(fill="x", pady=(0, 10))
        drop = ttk.Combobox(opt_frame, textvariable=aud_var, values=audiences, state="readonly", font=FONT_BODY)
        drop.pack(fill="both", expand=True, padx=5, pady=5)
        
        tk.Label(card_form, text="Message Body", font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 2))
        msg_frame = tk.Frame(card_form, bg=BG_COLOR, highlightbackground=BORDER_COLOR, highlightthickness=1)
        msg_frame.pack(fill="both", expand=True, pady=(0, 15))
        msg_text = tk.Text(msg_frame, bg=BG_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, 
                           relief="flat", font=FONT_BODY, bd=0, height=6, wrap="word")
        msg_text.pack(fill="both", expand=True, padx=8, pady=8)
        
        def publish_notice():
            title = title_entry.get().strip()
            target = aud_var.get()
            msg = msg_text.get("1.0", tk.END).strip()
            
            if not title or not msg:
                messagebox.showerror("Error", "Please fill in notification Title and Message.")
                return
                
            modify_db(
                "INSERT INTO notifications (title, message, target_role) VALUES (?, ?, ?)",
                (title, msg, target)
            )
            
            messagebox.showinfo("Success", f"Announcement published successfully for '{target}'!")
            title_entry.clear()
            msg_text.delete("1.0", tk.END)
            self.render_announcements() # Reload to show in list
            
        StyledButton(card_form, text="Publish Notice", command=publish_notice, variant="success").pack(fill="x")
        
        # Right Frame - List notices
        card_list = StyledCard(split)
        card_list.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        tk.Label(card_list, text="Active Announcements Board", font=FONT_SUBHEADING, bg=CARD_BG, fg=SUCCESS).pack(anchor="w", pady=(0, 10))
        
        notices_scroll = ScrollableFrame(card_list)
        notices_scroll.pack(fill="both", expand=True)
        
        notices = query_db("SELECT * FROM notifications ORDER BY created_at DESC")
        
        if not notices:
            tk.Label(notices_scroll.scrollable_frame, text="No active announcements logged.", font=FONT_BODY, bg=BG_COLOR, fg=TEXT_MUTED).pack(pady=20)
        else:
            for n in notices:
                nbox = tk.Frame(notices_scroll.scrollable_frame, bg=CARD_BG, highlightbackground=BORDER_COLOR, highlightthickness=1, pady=10, padx=12)
                nbox.pack(fill="x", pady=6)
                
                h = tk.Frame(nbox, bg=CARD_BG)
                h.pack(fill="x")
                tk.Label(h, text=n['title'], font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(side="left")
                tk.Label(h, text=f"For: {n['target_role']}", font=FONT_CAPTION, bg=CARD_BG, fg=LIGHT_ACCENT).pack(side="right")
                
                tk.Label(nbox, text=n['message'], font=FONT_BODY, bg=CARD_BG, fg=TEXT_MUTED, anchor="w", justify="left", wraplength=380).pack(fill="x", pady=(5, 5))
                
                ft = tk.Frame(nbox, bg=CARD_BG)
                ft.pack(fill="x")
                tk.Label(ft, text=f"Published: {n['created_at']}", font=FONT_CAPTION, bg=CARD_BG, fg=TEXT_MUTED).pack(side="left")
                
                def delete_notice(n_id=n['id']):
                    ans = messagebox.askyesno("Confirm Delete", "Permanently remove this notification?")
                    if ans:
                        modify_db("DELETE FROM notifications WHERE id = ?", (n_id,))
                        messagebox.showinfo("Success", "Notice removed from board.")
                        self.render_announcements()
                        
                StyledButton(ft, text="Delete", command=delete_notice, variant="danger", font=FONT_CAPTION, padx=6, pady=2).pack(side="right")
