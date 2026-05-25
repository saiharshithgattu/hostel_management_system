import tkinter as tk
from tkinter import messagebox, ttk
import datetime
from theme import *
from db import query_db, modify_db, get_db_connection

class WardenDashboard(tk.Frame):
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
            text="WARDEN PANEL", 
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
        self.tabs = ["Overview", "Visitor Logs", "Student Directory"]
        
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
        elif tab_name == "Visitor Logs":
            self.render_visitor_logs()
        elif tab_name == "Student Directory":
            self.render_student_directory()

    # ==================== OVERVIEW SCREEN ====================
    def render_overview(self):
        lbl_head = tk.Label(self.content_container, text="Warden Overview Board", font=FONT_HEADING, bg=BG_COLOR, fg=TEXT_COLOR)
        lbl_head.pack(anchor="w", pady=(0, 20))
        
        # Dynamic Warden stats
        total_students = query_db("SELECT count(*) as cnt FROM students", one=True)['cnt']
        active_visitors = query_db("SELECT count(*) as cnt FROM visitors WHERE check_out IS NULL", one=True)['cnt']
        total_rooms = query_db("SELECT count(*) as cnt FROM rooms", one=True)['cnt']
        full_rooms = query_db("SELECT count(*) as cnt FROM rooms WHERE current_occupancy >= capacity", one=True)['cnt']
        
        stats_frame = tk.Frame(self.content_container, bg=BG_COLOR)
        stats_frame.pack(fill="x", pady=(0, 20))
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)
        stats_frame.grid_columnconfigure(3, weight=1)
        
        # Stat cards
        cards_data = [
            ("Total Students", str(total_students), ACCENT_COLOR, 0),
            ("Active Visitors", str(active_visitors), WARNING, 1),
            ("Total Rooms", str(total_rooms), LIGHT_ACCENT, 2),
            ("Fully Occupied Rooms", str(full_rooms), SUCCESS, 3),
        ]
        
        for name, val, color, col in cards_data:
            card = StyledCard(stats_frame)
            card.grid(row=0, column=col, padx=4, sticky="ew")
            tk.Label(card, text=name, font=FONT_CAPTION, bg=CARD_BG, fg=TEXT_MUTED).pack(anchor="center")
            tk.Label(card, text=val, font=FONT_HEADING, bg=CARD_BG, fg=color).pack(anchor="center")
            
        # Split layout for notifications and recent activity
        split_frame = tk.Frame(self.content_container, bg=BG_COLOR)
        split_frame.pack(fill="both", expand=True)
        split_frame.grid_columnconfigure(0, weight=1)
        split_frame.grid_columnconfigure(1, weight=1)
        
        # Left Side - Active Warden Notices
        card_notices = StyledCard(split_frame)
        card_notices.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        tk.Label(card_notices, text="Warden & General Notices", font=FONT_SUBHEADING, bg=CARD_BG, fg=ACCENT_COLOR).pack(anchor="w", pady=(0, 15))
        
        notice_scroll = ScrollableFrame(card_notices)
        notice_scroll.pack(fill="both", expand=True)
        
        notices = query_db("SELECT * FROM notifications WHERE target_role IN ('All', 'Warden') ORDER BY created_at DESC")
        
        if not notices:
            tk.Label(notice_scroll.scrollable_frame, text="No active notices.", font=FONT_BODY, bg=BG_COLOR, fg=TEXT_MUTED).pack(pady=20)
        else:
            for n in notices:
                n_box = tk.Frame(notice_scroll.scrollable_frame, bg=BG_COLOR, highlightbackground=BORDER_COLOR, highlightthickness=1, pady=8, padx=10)
                n_box.pack(fill="x", pady=4)
                
                tk.Label(n_box, text=n['title'], font=FONT_BODY_BOLD, bg=BG_COLOR, fg=TEXT_COLOR, anchor="w").pack(fill="x")
                tk.Label(n_box, text=n['message'], font=FONT_BODY, bg=BG_COLOR, fg=TEXT_MUTED, anchor="w", justify="left", wraplength=300).pack(fill="x", pady=(2, 5))
                tk.Label(n_box, text=f"Posted: {n['created_at']}", font=FONT_CAPTION, bg=BG_COLOR, fg=TEXT_MUTED, anchor="w").pack(fill="x")

        # Right Side - Current Visitors Checklist
        card_visitors = StyledCard(split_frame)
        card_visitors.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        tk.Label(card_visitors, text="Active Visitors Roster", font=FONT_SUBHEADING, bg=CARD_BG, fg=WARNING).pack(anchor="w", pady=(0, 15))
        
        v_scroll = ScrollableFrame(card_visitors)
        v_scroll.pack(fill="both", expand=True)
        
        curr_visitors = query_db(
            """SELECT v.*, u.full_name as student_name, r.room_number 
               FROM visitors v 
               JOIN students s ON v.student_id = s.student_id 
               JOIN users u ON s.student_id = u.id 
               LEFT JOIN rooms r ON s.room_id = r.id 
               WHERE v.check_out IS NULL 
               ORDER BY v.check_in DESC"""
        )
        
        if not curr_visitors:
            tk.Label(v_scroll.scrollable_frame, text="No active visitors inside the hostel.", font=FONT_BODY, bg=BG_COLOR, fg=TEXT_MUTED).pack(pady=20)
        else:
            for cv in curr_visitors:
                cv_box = tk.Frame(v_scroll.scrollable_frame, bg=BG_COLOR, highlightbackground=BORDER_COLOR, highlightthickness=1, pady=8, padx=10)
                cv_box.pack(fill="x", pady=4)
                
                tk.Label(cv_box, text=f"{cv['visitor_name']} ({cv['relationship']})", font=FONT_BODY_BOLD, bg=BG_COLOR, fg=TEXT_COLOR, anchor="w").pack(fill="x")
                tk.Label(cv_box, text=f"Visiting: {cv['student_name']} (Rm {cv['room_number'] or 'N/A'})", font=FONT_BODY, bg=BG_COLOR, fg=TEXT_MUTED, anchor="w").pack(fill="x")
                tk.Label(cv_box, text=f"Checked In: {cv['check_in']}", font=FONT_CAPTION, bg=BG_COLOR, fg=TEXT_MUTED, anchor="w").pack(fill="x", pady=(2, 4))
                
                def checkout_fast(v_id=cv['id']):
                    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    modify_db("UPDATE visitors SET check_out = ? WHERE id = ?", (now_str, v_id))
                    messagebox.showinfo("Success", "Visitor checked out successfully!")
                    self.render_overview()
                    
                StyledButton(cv_box, text="Check Out", command=checkout_fast, variant="danger", font=FONT_CAPTION).pack(anchor="e")

    # ==================== VISITOR LOGS SCREEN ====================
    def render_visitor_logs(self):
        lbl_head = tk.Label(self.content_container, text="Visitor Register Management", font=FONT_HEADING, bg=BG_COLOR, fg=TEXT_COLOR)
        lbl_head.pack(anchor="w", pady=(0, 15))
        
        # Header actions
        action_frame = tk.Frame(self.content_container, bg=BG_COLOR)
        action_frame.pack(fill="x", pady=(0, 15))
        
        StyledButton(action_frame, text="+ Check-in New Visitor", command=self.open_visitor_checkin_modal, variant="primary").pack(side="left")
        
        # Table list of all visitor history
        visitor_logs = query_db(
            """SELECT v.*, u.full_name as student_name, r.room_number 
               FROM visitors v 
               JOIN students s ON v.student_id = s.student_id 
               JOIN users u ON s.student_id = u.id 
               LEFT JOIN rooms r ON s.room_id = r.id 
               ORDER BY v.check_in DESC"""
        )
        
        cols = [("Visitor Name", 2), ("Relationship", 1), ("Contact No", 2), ("Student Visited", 2), ("Room", 1), ("Check In Time", 2), ("Check Out Time", 2)]
        table = StyledTable(self.content_container, cols)
        table.pack(fill="both", expand=True)
        
        for vl in visitor_logs:
            out_time = vl['check_out'] if vl['check_out'] else "STILL INSIDE"
            row_data = [
                vl['visitor_name'],
                vl['relationship'],
                vl['contact'],
                vl['student_name'],
                f"Rm {vl['room_number'] or 'N/A'}",
                vl['check_in'],
                out_time
            ]
            row_frame = table.add_row(row_data, data=vl, on_click=self.on_visitor_row_click)
            
            # Highlight checkouts dynamically
            lbl_out = row_frame.winfo_children()[6]
            if not vl['check_out']:
                lbl_out.configure(fg=WARNING, font=FONT_BODY_BOLD)
            else:
                lbl_out.configure(fg=TEXT_MUTED)

    def on_visitor_row_click(self, visitor):
        if visitor['check_out']:
            messagebox.showinfo("Visitor Log Details", 
                                f"Visitor Name: {visitor['visitor_name']}\n"
                                f"Relationship: {visitor['relationship']}\n"
                                f"Contact: {visitor['contact']}\n"
                                f"Check-in: {visitor['check_in']}\n"
                                f"Check-out: {visitor['check_out']}")
            return
            
        # If still checked in, ask if they want to check them out
        ans = messagebox.askyesno("Check Out Visitor", f"Do you want to record Check-out for {visitor['visitor_name']}?")
        if ans:
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            modify_db("UPDATE visitors SET check_out = ? WHERE id = ?", (now_str, visitor['id']))
            messagebox.showinfo("Success", "Visitor checked out successfully!")
            self.render_visitor_logs()

    def open_visitor_checkin_modal(self):
        modal = tk.Toplevel(self)
        modal.title("New Visitor Check-in")
        modal.geometry("400x480")
        modal.configure(bg=BG_COLOR)
        modal.transient(self)
        modal.grab_set()
        
        # Center modal
        modal.update_idletasks()
        w = modal.winfo_width()
        h = modal.winfo_height()
        extra_x = int((self.winfo_screenwidth() - w) / 2)
        extra_y = int((self.winfo_screenheight() - h) / 2)
        modal.geometry(f"+{extra_x}+{extra_y}")
        
        tk.Label(modal, text="Log Visitor Entry", font=FONT_SUBHEADING, bg=BG_COLOR, fg=ACCENT_COLOR, pady=15).pack()
        
        form_frame = StyledCard(modal)
        form_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Fetch list of active students for dropdown
        students = query_db(
            """SELECT s.student_id, u.full_name, s.roll_number, r.room_number 
               FROM students s 
               JOIN users u ON s.student_id = u.id 
               LEFT JOIN rooms r ON s.room_id = r.id"""
        )
        
        tk.Label(form_frame, text="Select Student Visited", font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 2))
        
        # Build dropdown selection text array
        student_choices = [f"{s['full_name']} (Roll: {s['roll_number']}, Rm {s['room_number'] or 'N/A'})" for s in students]
        student_id_map = {f"{s['full_name']} (Roll: {s['roll_number']}, Rm {s['room_number'] or 'N/A'})": s['student_id'] for s in students}
        
        sel_student_var = tk.StringVar()
        dropdown_frame = tk.Frame(form_frame, bg=BG_COLOR, highlightbackground=BORDER_COLOR, highlightthickness=1)
        dropdown_frame.pack(fill="x", pady=(0, 10))
        
        drop = ttk.Combobox(dropdown_frame, textvariable=sel_student_var, values=student_choices, state="readonly", font=FONT_BODY)
        drop.pack(fill="both", expand=True, padx=5, pady=5)
        if student_choices:
            drop.current(0)
            
        tk.Label(form_frame, text="Visitor's Full Name", font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 2))
        name_entry = StyledEntry(form_frame, placeholder="Full name")
        name_entry.pack(fill="x", pady=(0, 10))
        
        tk.Label(form_frame, text="Relationship to Student", font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 2))
        rel_entry = StyledEntry(form_frame, placeholder="Father, Mother, Brother, etc.")
        rel_entry.pack(fill="x", pady=(0, 10))
        
        tk.Label(form_frame, text="Visitor Contact Phone", font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 2))
        contact_entry = StyledEntry(form_frame, placeholder="10-digit mobile number")
        contact_entry.pack(fill="x", pady=(0, 15))
        
        def save_visitor():
            student_sel = sel_student_var.get()
            name = name_entry.get().strip()
            rel = rel_entry.get().strip()
            contact = contact_entry.get().strip()
            
            if not student_sel or not name or not rel or not contact:
                messagebox.showerror("Error", "Please fill in all the visitor fields.")
                return
                
            student_id = student_id_map[student_sel]
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            modify_db(
                "INSERT INTO visitors (student_id, visitor_name, relationship, contact, check_in) VALUES (?, ?, ?, ?, ?)",
                (student_id, name, rel, contact, now_str)
            )
            
            modal.destroy()
            messagebox.showinfo("Success", f"Visitor entry logged successfully at {now_str}!")
            self.render_visitor_logs()
            
        StyledButton(form_frame, text="Submit Log Entry", command=save_visitor, variant="success").pack(fill="x", pady=(5, 5))
        StyledButton(form_frame, text="Cancel", command=modal.destroy, variant="secondary").pack(fill="x")

    # ==================== STUDENT DIRECTORY SCREEN ====================
    def render_student_directory(self):
        lbl_head = tk.Label(self.content_container, text="Student Contact & Emergency Directory", font=FONT_HEADING, bg=BG_COLOR, fg=TEXT_COLOR)
        lbl_head.pack(anchor="w", pady=(0, 15))
        
        # Search panel
        search_frame = StyledCard(self.content_container, padding=10)
        search_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(search_frame, text="Search Directory:", font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_MUTED).pack(side="left", padx=(0, 10))
        
        search_entry = StyledEntry(search_frame, placeholder="Search by name, roll, or branch...", width=30)
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Setup columns for contact details
        cols = [("Room", 1), ("Student Name", 2), ("Roll Number", 2), ("Branch", 2), ("Phone", 2), ("Parent Name", 2), ("Parent Contact", 2)]
        table = StyledTable(self.content_container, cols)
        table.pack(fill="both", expand=True)
        
        def load_directory(search_term=""):
            table.clear()
            
            query = """SELECT s.*, u.full_name, u.email, u.phone, r.room_number, r.block 
                       FROM students s 
                       JOIN users u ON s.student_id = u.id 
                       LEFT JOIN rooms r ON s.room_id = r.id"""
            args = ()
            
            if search_term:
                query += " WHERE u.full_name LIKE ? OR s.roll_number LIKE ? OR s.branch LIKE ? OR r.room_number LIKE ?"
                term = f"%{search_term}%"
                args = (term, term, term, term)
                
            query += " ORDER BY r.room_number ASC"
            
            student_dir = query_db(query, args)
            
            if not student_dir:
                # Add a notice row indicating no results
                tk.Label(table.scroll_frame.scrollable_frame, text="No matches found in directory.", font=FONT_BODY, bg=BG_COLOR, fg=TEXT_MUTED).pack(pady=20)
            else:
                for sd in student_dir:
                    row_data = [
                        f"Rm {sd['room_number'] or 'N/A'} ({sd['block'] or ''})",
                        sd['full_name'],
                        sd['roll_number'],
                        sd['branch'] or "N/A",
                        sd['phone'] or "N/A",
                        sd['parent_name'] or "N/A",
                        sd['parent_phone'] or "N/A"
                    ]
                    table.add_row(row_data, data=sd)
                    
        # Instant Search event
        search_entry.entry.bind("<KeyRelease>", lambda e: load_directory(search_entry.get().strip()))
        
        # Initial directory load
        load_directory()
