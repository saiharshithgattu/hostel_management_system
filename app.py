import tkinter as tk
from tkinter import messagebox, ttk
from theme import *
from db import init_db
from auth import login_user
from admin_dashboard import AdminDashboard
from student_dashboard import StudentDashboard
from warden_dashboard import WardenDashboard

class HostelApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Initialize SQLite database schema
        init_db()
        
        # Configure Root Window Properties
        self.title("Elite Hostel Management Suite")
        self.geometry("1200x750")
        self.minimum_size = (1000, 650)
        self.minsize(*self.minimum_size)
        self.configure(bg=BG_COLOR)
        
        # Apply Global ttk styles
        apply_global_styles(self)
        
        # Center the window on the screen
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        extra_x = int((self.winfo_screenwidth() - w) / 2)
        extra_y = int((self.winfo_screenheight() - h) / 2)
        self.geometry(f"+{extra_x}+{extra_y}")
        
        # Active Frame Container
        self.current_frame = None
        
        # Start at Login screen
        self.show_login_screen()
        
    def clear_current_frame(self):
        if self.current_frame:
            # Clean up all widgets safely
            self.current_frame.destroy()
            self.current_frame = None
            
    def show_login_screen(self):
        self.clear_current_frame()
        self.title("Hostel Hub - Secure Access Terminal")
        
        # Create Login Page Layout Container
        self.current_frame = tk.Frame(self, bg=BG_COLOR)
        self.current_frame.pack(fill="both", expand=True)
        
        # Grid weighting to center the Login card
        self.current_frame.grid_columnconfigure(0, weight=1)
        self.current_frame.grid_rowconfigure(0, weight=1)
        
        # Center card container
        login_card = StyledCard(self.current_frame, padding=35, border_width=1)
        login_card.grid(row=0, column=0, sticky="")
        
        # Logo Icon and Heading
        lbl_logo = tk.Label(
            login_card, 
            text="🏨 ELITE HOSTELS", 
            font=FONT_HEADING, 
            bg=CARD_BG, 
            fg=ACCENT_COLOR
        )
        lbl_logo.pack(pady=10)
        
        lbl_sub = tk.Label(
            login_card, 
            text="Secure Portal Gateway", 
            font=FONT_BODY, 
            bg=CARD_BG, 
            fg=TEXT_MUTED
        )
        lbl_sub.pack(pady=(0, 20))
        
        # 1. Username Field
        tk.Label(login_card, text="Username / Account ID", font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 2))
        ent_username = StyledEntry(login_card, placeholder="Enter your username")
        ent_username.pack(fill="x", pady=(0, 15))
        
        # 2. Password Field
        tk.Label(login_card, text="Access Password", font=FONT_BODY_BOLD, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(5, 2))
        ent_password = StyledEntry(login_card, placeholder="Enter your password", show="•")
        ent_password.pack(fill="x", pady=(0, 10))
        
        # Show/Hide Password Checkbutton
        show_pwd_var = tk.BooleanVar(value=False)
        
        def custom_focus_out(event):
            ent_password.configure(highlightbackground=BORDER_COLOR)
            if not ent_password.entry.get():
                ent_password.entry.insert(0, ent_password.placeholder)
                ent_password.entry.configure(fg=TEXT_MUTED, show="")
            else:
                if not show_pwd_var.get():
                    ent_password.entry.configure(show="•")
                    
        def custom_focus_in(event):
            ent_password.configure(highlightbackground=ACCENT_COLOR)
            if ent_password.entry.get() == ent_password.placeholder:
                ent_password.entry.delete(0, tk.END)
                ent_password.entry.configure(fg=TEXT_COLOR)
                if not show_pwd_var.get():
                    ent_password.entry.configure(show="•")
                    
        # Bind overrides to support show/hide seamlessly with placeholder text
        ent_password.entry.bind("<FocusIn>", custom_focus_in)
        ent_password.entry.bind("<FocusOut>", custom_focus_out)
        
        def handle_toggle():
            if ent_password.entry.get() == ent_password.placeholder:
                ent_password.entry.configure(show="")
            else:
                if show_pwd_var.get():
                    ent_password.entry.configure(show="")
                else:
                    ent_password.entry.configure(show="•")
                    
        chk_show_pwd = tk.Checkbutton(
            login_card,
            text="Show Password",
            variable=show_pwd_var,
            command=handle_toggle,
            bg=CARD_BG,
            fg=TEXT_MUTED,
            selectcolor=BG_COLOR,
            activebackground=CARD_BG,
            activeforeground=TEXT_COLOR,
            font=FONT_CAPTION,
            bd=0,
            relief="flat",
            cursor="hand2"
        )
        chk_show_pwd.pack(anchor="w", pady=(0, 20))
        
        # Focus on username by default
        ent_username.entry.focus_set()
        
        # Action handler
        def handle_login():
            username = ent_username.get().strip()
            password = ent_password.get().strip()
            
            if not username or not password:
                show_toast("Please specify both Username and Password fields.", "danger")
                return
                
            user = login_user(username, password)
            if user:
                show_toast("Access authorized! Generating dashboard...", "success")
                self.after(800, lambda: self.show_dashboard_screen(user))
            else:
                show_toast("Invalid credentials. Access rejected.", "danger")
                ent_password.clear()
                
        # Bind Return Key to login
        self.bind("<Return>", lambda e: handle_login())
        
        # Login Button
        btn_login = StyledButton(login_card, text="Verify Identity", command=handle_login, variant="primary")
        btn_login.pack(fill="x", pady=(0, 10))
        
        # Elegant Toast alerts built inside the card
        self.toast_lbl = tk.Label(login_card, text="", font=FONT_BODY, bg=CARD_BG, fg=TEXT_MUTED, wraplength=280)
        self.toast_lbl.pack(fill="x", pady=(5, 0))
        
        def show_toast(message, variant="info"):
            fg_color = SUCCESS if variant == "success" else (DANGER if variant == "danger" else TEXT_MUTED)
            self.toast_lbl.configure(text=message, fg=fg_color)
            
    def show_dashboard_screen(self, user):
        self.clear_current_frame()
        self.unbind("<Return>")
        
        role = user['role']
        self.title(f"{role} Workspace - Elite Hostel Suite")
        
        # Router to Dashboard Roles
        if role == "Admin":
            self.current_frame = AdminDashboard(self, user, on_logout=self.show_login_screen)
        elif role == "Warden":
            self.current_frame = WardenDashboard(self, user, on_logout=self.show_login_screen)
        elif role == "Student":
            self.current_frame = StudentDashboard(self, user, on_logout=self.show_login_screen)
            
        self.current_frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = HostelApp()
    app.mainloop()
