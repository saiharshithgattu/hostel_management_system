import tkinter as tk
from tkinter import messagebox, ttk
import datetime
from theme import *
from db import query_db, modify_db, get_db_connection

class StudentDashboard(tk.Frame):
    def __init__(self, parent, user, on_logout):
        super().__init__(parent, bg=BG_COLOR)
        self.user = user
        self.on_logout = on_logout
        
        # Load detailed student profile
        self.student_profile = query_db(
            """SELECT s.*, r.room_number, r.block, r.monthly_rent 
               FROM students s 
               LEFT JOIN rooms r ON s.room_id = r.id 
               WHERE s.student_id = ?""",
            (self.user['id'],),
            one=True
        )
        
        # Sidebar Navigation
        self.sidebar = tk.Frame(self, bg=NAV_BG, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Sidebar Header (Logo/Title)
        lbl_logo = tk.Label(
            self.sidebar, 
            text="STUDENT PANEL", 
            bg=NAV_BG, 
            fg=ACCENT_COLOR, 
            font=FONT_SUBHEADING, 
            pady=20
        )
        lbl_logo.pack(fill="x")
        
        # User details card in sidebar
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
        self.tabs = ["Profile", "Fee Log", "Support", "Noticeboard"]
        
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
        self.switch_tab("Profile")
        
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
        if tab_name == "Profile":
            self.render_profile()
        elif tab_name == "Fee Log":
            self.render_fee_log()
        elif tab_name == "Support":
            self.render_support()
        elif tab_name == "Noticeboard":
            self.render_noticeboard()

    # ==================== PROFILE SCREEN ====================
    def render_profile(self):
        # Heading
        lbl_head = tk.Label(self.content_container, text="My Profile", font=FONT_HEADING, bg=BG_COLOR, fg=TEXT_COLOR)
        lbl_head.pack(anchor="w", pady=(0, 20))
        
        # Flex layout for Profile Card and Room Details
        cards_frame = tk.Frame(self.content_container, bg=BG_COLOR)
        cards_frame.pack(fill="both", expand=True)
        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)
        
        # Card 1: Personal Information
        card_personal = StyledCard(cards_frame)
        card_personal.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        tk.Label(card_personal, text="Personal Details", font=FONT_SUBHEADING, bg=CARD_BG, fg=ACCENT_COLOR).pack(anchor="w", pady=(0, 15))
        
        details = [
            ("Full Name:", self.user['full_name']),
            ("Roll Number:", self.student_profile['roll_number'] if self.student_profile else "N/A"),
            ("Branch:", self.student_profile['branch'] if self.student_profile else "N/A"),
            ("Username:", self.user['username']),
            ("Email:", self.user['email'] or "N/A"),
            ("Phone:", self.user['phone'] or "N/A"),
            ("Admission Date:", self.student_profile['admission_date'] if self.student_profile else "N/A"),
            ("Parent Name:", self.student_profile['parent_name'] if self.student_profile else "N/A"),
            ("Parent Contact:", self.student_profile['parent_phone'] if self.student_profile else "N/A"),
        ]
        
        for label, val in details:
            row = tk.Frame(card_personal, bg=CARD_BG, pady=5)
            row.pack(fill="x")
            tk.Label(row, text=label, font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_MUTED, width=15, anchor="w").pack(side="left")
            tk.Label(row, text=val, font=FONT_BODY, bg=CARD_BG, fg=TEXT_COLOR, anchor="w").pack(side="left", fill="x", expand=True)
            
        # Card 2: Room & Roommates Information
        card_room = StyledCard(cards_frame)
        card_room.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        tk.Label(card_room, text="Room Allotment", font=FONT_SUBHEADING, bg=CARD_BG, fg=SUCCESS).pack(anchor="w", pady=(0, 15))
        
        if self.student_profile and self.student_profile['room_number']:
            # Room Details
            r_details = [
                ("Room Number:", self.student_profile['room_number']),
                ("Block:", f"Block {self.student_profile['block']}"),
                ("Monthly Rent:", f"₹{self.student_profile['monthly_rent']:.2f}")
            ]
            for label, val in r_details:
                row = tk.Frame(card_room, bg=CARD_BG, pady=4)
                row.pack(fill="x")
                tk.Label(row, text=label, font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_MUTED, width=15, anchor="w").pack(side="left")
                tk.Label(row, text=val, font=FONT_BODY, bg=CARD_BG, fg=TEXT_COLOR).pack(side="left")
                
            tk.Label(card_room, text="My Roommates", font=FONT_BODY_BOLD, bg=CARD_BG, fg=LIGHT_ACCENT).pack(anchor="w", pady=(15, 5))
            
            # Fetch roommates
            roommates = query_db(
                """SELECT u.full_name, u.email, u.phone, s.roll_number 
                   FROM students s 
                   JOIN users u ON s.student_id = u.id 
                   WHERE s.room_id = ? AND s.student_id != ?""",
                (self.student_profile['room_id'], self.user['id'])
            )
            
            if roommates:
                for rm in roommates:
                    rm_frame = tk.Frame(card_room, bg=CARD_BG, highlightbackground=BORDER_COLOR, highlightthickness=1, pady=6, padx=8)
                    rm_frame.pack(fill="x", pady=4)
                    
                    tk.Label(rm_frame, text=rm['full_name'], font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w")
                    tk.Label(rm_frame, text=f"Roll: {rm['roll_number']} | Phone: {rm['phone'] or 'N/A'}", font=FONT_CAPTION, bg=CARD_BG, fg=TEXT_MUTED).pack(anchor="w")
            else:
                tk.Label(card_room, text="No roommates in this room.", font=FONT_BODY, bg=CARD_BG, fg=TEXT_MUTED, pady=10).pack(anchor="w")
        else:
            tk.Label(card_room, text="No Room Assigned Yet", font=FONT_SUBHEADING, bg=CARD_BG, fg=WARNING, pady=20).pack(anchor="center")
            tk.Label(card_room, text="Please contact the hostel administrator for room allocation.", font=FONT_BODY, bg=CARD_BG, fg=TEXT_MUTED, justify="center").pack(anchor="center")

    # ==================== FEE LOG SCREEN ====================
    def render_fee_log(self):
        lbl_head = tk.Label(self.content_container, text="Fee Log & Payments", font=FONT_HEADING, bg=BG_COLOR, fg=TEXT_COLOR)
        lbl_head.pack(anchor="w", pady=(0, 15))
        
        # Summary Header Cards
        fees = query_db("SELECT * FROM fees WHERE student_id = ? ORDER BY due_date DESC", (self.user['id'],))
        
        total_billed = sum(f['amount_total'] for f in fees)
        total_paid = sum(f['amount_paid'] for f in fees)
        total_due = sum(f['amount_due'] for f in fees)
        
        sum_frame = tk.Frame(self.content_container, bg=BG_COLOR)
        sum_frame.pack(fill="x", pady=(0, 20))
        sum_frame.grid_columnconfigure(0, weight=1)
        sum_frame.grid_columnconfigure(1, weight=1)
        sum_frame.grid_columnconfigure(2, weight=1)
        
        # Card Billed
        c_billed = StyledCard(sum_frame)
        c_billed.grid(row=0, column=0, padx=(0, 8), sticky="ew")
        tk.Label(c_billed, text="Total Billed", font=FONT_CAPTION, bg=CARD_BG, fg=TEXT_MUTED).pack(anchor="center")
        tk.Label(c_billed, text=f"₹{total_billed:.2f}", font=FONT_SUBHEADING, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="center")
        
        # Card Paid
        c_paid = StyledCard(sum_frame)
        c_paid.grid(row=0, column=1, padx=4, sticky="ew")
        tk.Label(c_paid, text="Total Paid", font=FONT_CAPTION, bg=CARD_BG, fg=TEXT_MUTED).pack(anchor="center")
        tk.Label(c_paid, text=f"₹{total_paid:.2f}", font=FONT_SUBHEADING, bg=CARD_BG, fg=SUCCESS).pack(anchor="center")
        
        # Card Due
        c_due = StyledCard(sum_frame)
        c_due.grid(row=0, column=2, padx=(8, 0), sticky="ew")
        tk.Label(c_due, text="Total Due", font=FONT_CAPTION, bg=CARD_BG, fg=TEXT_MUTED).pack(anchor="center")
        tk.Label(c_due, text=f"₹{total_due:.2f}", font=FONT_SUBHEADING, bg=CARD_BG, fg=DANGER).pack(anchor="center")
        
        # Bills List
        lbl_sub = tk.Label(self.content_container, text="All Bills", font=FONT_SUBHEADING, bg=BG_COLOR, fg=TEXT_COLOR)
        lbl_sub.pack(anchor="w", pady=(0, 10))
        
        cols = [("Billing Period", 2), ("Total Amount", 2), ("Amount Paid", 2), ("Amount Due", 2), ("Status", 2), ("Due Date", 2)]
        table = StyledTable(self.content_container, cols)
        table.pack(fill="both", expand=True)
        
        for f in fees:
            status_text = f['status']
            row_data = [
                f['billing_period'],
                f"₹{f['amount_total']:.2f}",
                f"₹{f['amount_paid']:.2f}",
                f"₹{f['amount_due']:.2f}",
                status_text,
                f['due_date']
            ]
            row_frame = table.add_row(row_data, data=f, on_click=self.on_bill_click)
            
            # Color status text dynamically
            lbl_status = row_frame.winfo_children()[4]
            if status_text == "Paid":
                lbl_status.configure(fg=SUCCESS, font=FONT_BODY_BOLD)
            elif status_text == "Partially Paid":
                lbl_status.configure(fg=WARNING, font=FONT_BODY_BOLD)
            else:
                lbl_status.configure(fg=DANGER, font=FONT_BODY_BOLD)
                
    def on_bill_click(self, fee):
        if fee['status'] == "Paid":
            messagebox.showinfo("Bill Paid", f"This bill for {fee['billing_period']} is already fully paid. Thank you!")
            return
            
        # Open Mock Payment Modal
        pay_modal = tk.Toplevel(self)
        pay_modal.title("Pay Bill")
        pay_modal.geometry("380x360")
        pay_modal.configure(bg=BG_COLOR)
        pay_modal.transient(self)
        pay_modal.grab_set()
        
        # Centering the modal
        pay_modal.update_idletasks()
        w = pay_modal.winfo_width()
        h = pay_modal.winfo_height()
        extra_x = int((self.winfo_screenwidth() - w) / 2)
        extra_y = int((self.winfo_screenheight() - h) / 2)
        pay_modal.geometry(f"+{extra_x}+{extra_y}")
        
        tk.Label(pay_modal, text="Secure Payment Simulator", font=FONT_SUBHEADING, bg=BG_COLOR, fg=ACCENT_COLOR, pady=15).pack()
        
        detail_frame = StyledCard(pay_modal)
        detail_frame.pack(fill="x", padx=20, pady=10)
        
        fields = [
            ("Billing Period:", fee['billing_period']),
            ("Total Due:", f"₹{fee['amount_due']:.2f}"),
        ]
        for lbl, val in fields:
            r = tk.Frame(detail_frame, bg=CARD_BG, pady=2)
            r.pack(fill="x")
            tk.Label(r, text=lbl, font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_MUTED, width=15, anchor="w").pack(side="left")
            tk.Label(r, text=val, font=FONT_BODY, bg=CARD_BG, fg=TEXT_COLOR).pack(side="left")
            
        tk.Label(pay_modal, text="Enter Payment Amount (₹):", font=FONT_BODY_BOLD, bg=BG_COLOR, fg=TEXT_COLOR, anchor="w").pack(fill="x", padx=20, pady=(10, 2))
        
        amount_entry = StyledEntry(pay_modal, placeholder=str(fee['amount_due']))
        amount_entry.pack(fill="x", padx=20, pady=(0, 15))
        
        def process_payment():
            try:
                pay_amt = float(amount_entry.get())
                if pay_amt <= 0:
                    raise ValueError("Amount must be positive.")
                if pay_amt > fee['amount_due']:
                    raise ValueError("Cannot pay more than the outstanding due amount.")
            except ValueError as ve:
                messagebox.showerror("Invalid Input", str(ve) or "Please enter a valid numeric amount.")
                return
                
            # Perform SQLite Update
            new_paid = fee['amount_paid'] + pay_amt
            new_due = fee['amount_total'] - new_paid
            new_status = "Paid" if new_due == 0 else "Partially Paid"
            
            modify_db(
                "UPDATE fees SET amount_paid = ?, amount_due = ?, status = ? WHERE id = ?",
                (new_paid, new_due, new_status, fee['id'])
            )
            
            # Show payment details summary
            pay_modal.destroy()
            messagebox.showinfo("Payment Successful", f"Successfully paid ₹{pay_amt:.2f} for {fee['billing_period']}!\nOutstanding due: ₹{new_due:.2f}")
            self.render_fee_log() # Refresh tab
            
        StyledButton(pay_modal, text="Simulate Payment", command=process_payment, variant="success").pack(fill="x", padx=20, pady=10)
        StyledButton(pay_modal, text="Cancel", command=pay_modal.destroy, variant="secondary").pack(fill="x", padx=20)

    # ==================== SUPPORT & FEEDBACK SCREEN ====================
    def render_support(self):
        # We need a grid split layout: Left side = Post Feedback form, Right side = History of tickets
        lbl_head = tk.Label(self.content_container, text="Feedback & Maintenance Support", font=FONT_HEADING, bg=BG_COLOR, fg=TEXT_COLOR)
        lbl_head.pack(anchor="w", pady=(0, 20))
        
        split_frame = tk.Frame(self.content_container, bg=BG_COLOR)
        split_frame.pack(fill="both", expand=True)
        split_frame.grid_columnconfigure(0, weight=2)
        split_frame.grid_columnconfigure(1, weight=3)
        
        # Left Side - Raise Complaint Card
        card_form = StyledCard(split_frame)
        card_form.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        tk.Label(card_form, text="Submit Feedback / Complaint", font=FONT_SUBHEADING, bg=CARD_BG, fg=ACCENT_COLOR).pack(anchor="w", pady=(0, 15))
        
        tk.Label(card_form, text="Category", font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 2))
        categories = ["Maintenance", "Food", "Cleanliness", "Security", "Other"]
        cat_var = tk.StringVar(value=categories[0])
        
        # Styled OptionMenu wrapper inside flat frame
        opt_frame = tk.Frame(card_form, bg=BG_COLOR, highlightbackground=BORDER_COLOR, highlightthickness=1)
        opt_frame.pack(fill="x", pady=(0, 10))
        
        opt_menu = ttk.Combobox(opt_frame, textvariable=cat_var, values=categories, state="readonly", font=FONT_BODY)
        opt_menu.pack(fill="both", expand=True, padx=5, pady=5)
        
        tk.Label(card_form, text="Subject", font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 2))
        subj_entry = StyledEntry(card_form, placeholder="Brief summary of issue")
        subj_entry.pack(fill="x", pady=(0, 10))
        
        tk.Label(card_form, text="Detailed Message", font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 2))
        
        # Styled Message Text area
        msg_frame = tk.Frame(card_form, bg=BG_COLOR, highlightbackground=BORDER_COLOR, highlightthickness=1)
        msg_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        msg_text = tk.Text(msg_frame, bg=BG_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, 
                           relief="flat", font=FONT_BODY, bd=0, height=5, wrap="word")
        msg_text.pack(fill="both", expand=True, padx=8, pady=8)
        
        def submit_feedback():
            cat = cat_var.get()
            subj = subj_entry.get().strip()
            msg = msg_text.get("1.0", tk.END).strip()
            
            if not subj or not msg:
                messagebox.showerror("Error", "Please fill in all the feedback fields.")
                return
                
            modify_db(
                "INSERT INTO feedback (student_id, category, subject, message) VALUES (?, ?, ?, ?)",
                (self.user['id'], cat, subj, msg)
            )
            
            messagebox.showinfo("Success", "Your feedback ticket has been logged successfully!")
            subj_entry.clear()
            msg_text.delete("1.0", tk.END)
            self.render_support() # Reload UI split screen to show history
            
        StyledButton(card_form, text="Submit Ticket", command=submit_feedback, variant="primary").pack(fill="x")
        
        # Right Side - Past Feedback History Card
        card_history = StyledCard(split_frame)
        card_history.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        tk.Label(card_history, text="My Support History", font=FONT_SUBHEADING, bg=CARD_BG, fg=SUCCESS).pack(anchor="w", pady=(0, 10))
        
        history_list = ScrollableFrame(card_history)
        history_list.pack(fill="both", expand=True)
        
        tickets = query_db(
            "SELECT * FROM feedback WHERE student_id = ? ORDER BY created_at DESC",
            (self.user['id'],)
        )
        
        if not tickets:
            tk.Label(history_list.scrollable_frame, text="No feedback tickets logged yet.", font=FONT_BODY, bg=BG_COLOR, fg=TEXT_MUTED).pack(pady=20)
        else:
            for t in tickets:
                ticket_box = tk.Frame(history_list.scrollable_frame, bg=CARD_BG, highlightbackground=BORDER_COLOR, highlightthickness=1, pady=10, padx=12)
                ticket_box.pack(fill="x", pady=6)
                
                # Header row: Category / Date
                header_row = tk.Frame(ticket_box, bg=CARD_BG)
                header_row.pack(fill="x")
                
                tk.Label(header_row, text=f"[{t['category']}]", font=FONT_BODY_BOLD, bg=CARD_BG, fg=LIGHT_ACCENT).pack(side="left")
                
                # Dynamic colored status badge
                status = t['status']
                s_color = SUCCESS if status == "Resolved" else (WARNING if status == "Reviewed" else TEXT_MUTED)
                tk.Label(header_row, text=status, font=FONT_BODY_BOLD, bg=CARD_BG, fg=s_color).pack(side="right")
                
                # Subject & Message
                tk.Label(ticket_box, text=t['subject'], font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR, anchor="w").pack(fill="x", pady=(5, 2))
                tk.Label(ticket_box, text=t['message'], font=FONT_BODY, bg=CARD_BG, fg=TEXT_MUTED, justify="left", anchor="w", wraplength=400).pack(fill="x", pady=(0, 5))
                
                # Admin response section if resolved
                if t['admin_response']:
                    resp_box = tk.Frame(ticket_box, bg=BG_COLOR, highlightbackground=BORDER_COLOR, highlightthickness=1, pady=6, padx=8)
                    resp_box.pack(fill="x", pady=(5, 0))
                    tk.Label(resp_box, text="Response from Admin:", font=FONT_CAPTION, bg=BG_COLOR, fg=SUCCESS).pack(anchor="w")
                    tk.Label(resp_box, text=t['admin_response'], font=FONT_BODY, bg=BG_COLOR, fg=TEXT_COLOR, justify="left", anchor="w", wraplength=380).pack(fill="x")
                    
                # Date caption footer
                tk.Label(ticket_box, text=f"Submitted on: {t['created_at']}", font=FONT_CAPTION, bg=CARD_BG, fg=TEXT_MUTED, anchor="w").pack(fill="x", pady=(5, 0))

    # ==================== NOTICEBOARD SCREEN ====================
    def render_noticeboard(self):
        lbl_head = tk.Label(self.content_container, text="Official Announcements", font=FONT_HEADING, bg=BG_COLOR, fg=TEXT_COLOR)
        lbl_head.pack(anchor="w", pady=(0, 20))
        
        board = ScrollableFrame(self.content_container)
        board.pack(fill="both", expand=True)
        
        # Query notices targeted for 'All' or 'Student'
        notices = query_db(
            "SELECT * FROM notifications WHERE target_role IN ('All', 'Student') ORDER BY created_at DESC"
        )
        
        if not notices:
            tk.Label(board.scrollable_frame, text="No active notices at the moment.", font=FONT_BODY, bg=BG_COLOR, fg=TEXT_MUTED).pack(pady=30)
        else:
            for n in notices:
                notice_card = StyledCard(board.scrollable_frame)
                notice_card.pack(fill="x", pady=8, padx=5)
                
                header = tk.Frame(notice_card, bg=CARD_BG)
                header.pack(fill="x", pady=(0, 8))
                
                tk.Label(header, text=n['title'], font=FONT_SUBHEADING, bg=CARD_BG, fg=ACCENT_COLOR).pack(side="left")
                tk.Label(header, text=n['created_at'], font=FONT_CAPTION, bg=CARD_BG, fg=TEXT_MUTED).pack(side="right")
                
                divider = tk.Frame(notice_card, height=1, bg=BORDER_COLOR)
                divider.pack(fill="x", pady=(0, 8))
                
                tk.Label(
                    notice_card, 
                    text=n['message'], 
                    font=FONT_BODY, 
                    bg=CARD_BG, 
                    fg=TEXT_COLOR, 
                    justify="left", 
                    anchor="w", 
                    wraplength=650
                ).pack(fill="x")
