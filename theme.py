import tkinter as tk
from tkinter import ttk

# Colors - Modern Dark Slate Palette
BG_COLOR = "#0F172A"       # Deep Slate 900
CARD_BG = "#1E293B"        # Slate 800
NAV_BG = "#0B0F19"         # Very dark slate
TEXT_COLOR = "#F8FAFC"     # White Slate 50
TEXT_MUTED = "#94A3B8"     # Muted Slate 400
ACCENT_COLOR = "#6366F1"   # Indigo 500
ACCENT_HOVER = "#4F46E5"   # Indigo 600
SUCCESS = "#10B981"        # Emerald 500
WARNING = "#F59E0B"        # Amber 500
DANGER = "#EF4444"         # Red 500
BORDER_COLOR = "#334155"   # Slate 700
LIGHT_ACCENT = "#818CF8"   # Indigo 400

# Fonts
FONT_HEADING = ("Segoe UI", 20, "bold")
FONT_SUBHEADING = ("Segoe UI", 14, "bold")
FONT_BODY = ("Segoe UI", 11, "normal")
FONT_BODY_BOLD = ("Segoe UI", 11, "bold")
FONT_CAPTION = ("Segoe UI", 9, "normal")
FONT_CODE = ("Consolas", 10, "normal")

def apply_global_styles(root):
    """Sets default styles and configurations for the Tkinter app."""
    # We configure the ttk style if any standard ttk widgets are used
    style = ttk.Style(root)
    style.theme_use("clam")
    
    # Configure scrollbars globally
    style.configure("TScrollbar", gripcount=0, background=BORDER_COLOR, 
                    troughcolor=BG_COLOR, bordercolor=BG_COLOR, arrowcolor=TEXT_MUTED)
    style.map("TScrollbar", background=[('active', ACCENT_COLOR)])
    
    # Notebook styles
    style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
    style.configure("TNotebook.Tab", background=CARD_BG, foreground=TEXT_MUTED, 
                    font=FONT_BODY_BOLD, padding=[15, 8], borderwidth=0)
    style.map("TNotebook.Tab", background=[('selected', ACCENT_COLOR)], 
              foreground=[('selected', TEXT_COLOR)])

class StyledCard(tk.Frame):
    """A beautiful dark card container with border styling and padding."""
    def __init__(self, parent, padding=15, border_width=1, **kwargs):
        super().__init__(
            parent, 
            bg=CARD_BG, 
            highlightbackground=BORDER_COLOR, 
            highlightthickness=border_width,
            padx=padding, 
            pady=padding, 
            **kwargs
        )

class StyledButton(tk.Button):
    """A clean, flat, modern button with interactive hover effects."""
    def __init__(self, parent, text, command=None, variant="primary", font=FONT_BODY_BOLD, **kwargs):
        self.variant = variant
        if variant == "primary":
            bg = ACCENT_COLOR
            fg = TEXT_COLOR
            active_bg = ACCENT_HOVER
        elif variant == "secondary":
            bg = BORDER_COLOR
            fg = TEXT_COLOR
            active_bg = "#475569" # Slate 600
        elif variant == "success":
            bg = SUCCESS
            fg = TEXT_COLOR
            active_bg = "#059669" # Emerald 600
        elif variant == "danger":
            bg = DANGER
            fg = TEXT_COLOR
            active_bg = "#DC2626" # Red 600
        elif variant == "warning":
            bg = WARNING
            fg = BG_COLOR
            active_bg = "#D97706" # Amber 600
        else:  # Custom/Outline style
            bg = CARD_BG
            fg = ACCENT_COLOR
            active_bg = BORDER_COLOR
            
        super().__init__(
            parent, 
            text=text, 
            command=command, 
            bg=bg, 
            fg=fg, 
            activebackground=active_bg, 
            activeforeground=fg, 
            relief="flat", 
            font=font, 
            cursor="hand2", 
            bd=0, 
            padx=15, 
            pady=8,
            **kwargs
        )
        
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        
    def on_hover(self, event):
        if self.variant == "primary":
            self.configure(bg=ACCENT_HOVER)
        elif self.variant == "secondary":
            self.configure(bg="#475569")
        elif self.variant == "success":
            self.configure(bg="#059669")
        elif self.variant == "danger":
            self.configure(bg="#DC2626")
        elif self.variant == "warning":
            self.configure(bg="#D97706")
            
    def on_leave(self, event):
        if self.variant == "primary":
            self.configure(bg=ACCENT_COLOR)
        elif self.variant == "secondary":
            self.configure(bg=BORDER_COLOR)
        elif self.variant == "success":
            self.configure(bg=SUCCESS)
        elif self.variant == "danger":
            self.configure(bg=DANGER)
        elif self.variant == "warning":
            self.configure(bg=WARNING)

class StyledEntry(tk.Frame):
    """An input field wrapped in a modern card-like frame with glow on focus."""
    def __init__(self, parent, placeholder="", show="", font=FONT_BODY, width=20, **kwargs):
        super().__init__(parent, bg=BG_COLOR, highlightbackground=BORDER_COLOR, highlightthickness=1)
        self.placeholder = placeholder
        self.show = show
        
        self.entry = tk.Entry(
            self, 
            bg=BG_COLOR, 
            fg=TEXT_COLOR, 
            insertbackground=TEXT_COLOR, 
            relief="flat", 
            font=font, 
            width=width,
            **kwargs
        )
        
        if show:
            self.entry.configure(show=show)
            
        self.entry.pack(fill="both", expand=True, padx=10, pady=8)
        
        # Setup placeholder behavior
        if placeholder:
            self.entry.insert(0, placeholder)
            self.entry.configure(fg=TEXT_MUTED)
            self.entry.bind("<FocusIn>", self.on_focus_in)
            self.entry.bind("<FocusOut>", self.on_focus_out)
        else:
            self.entry.bind("<FocusIn>", lambda e: self.configure(highlightbackground=ACCENT_COLOR))
            self.entry.bind("<FocusOut>", lambda e: self.configure(highlightbackground=BORDER_COLOR))
            
    def on_focus_in(self, event):
        self.configure(highlightbackground=ACCENT_COLOR)
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.configure(fg=TEXT_COLOR)
            if self.show:
                self.entry.configure(show=self.show)
                
    def on_focus_out(self, event):
        self.configure(highlightbackground=BORDER_COLOR)
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.configure(fg=TEXT_MUTED)
            if self.show:
                self.entry.configure(show="")
                
    def get(self):
        val = self.entry.get()
        if val == self.placeholder:
            return ""
        return val
        
    def set(self, text):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)
        self.entry.configure(fg=TEXT_COLOR)
        
    def clear(self):
        self.entry.delete(0, tk.END)
        if self.placeholder:
            self.entry.insert(0, self.placeholder)
            self.entry.configure(fg=TEXT_MUTED)

class ScrollableFrame(tk.Frame):
    """A highly dynamic scrollable frame built inside standard Tkinter."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG_COLOR, **kwargs)
        
        self.canvas = tk.Canvas(self, bg=BG_COLOR, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=BG_COLOR)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Make frame adjust to canvas width
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Mousewheel scroll support
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        
    def _on_mousewheel(self, event):
        # Only scroll if window still exists and mouse cursor is over it
        try:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        except Exception:
            pass

class StyledTable(tk.Frame):
    """An elegant list/table component with modern rows, alternating colors, and custom header columns."""
    def __init__(self, parent, columns, show_headers=True, **kwargs):
        super().__init__(parent, bg=BG_COLOR, **kwargs)
        self.columns = columns
        self.rows = []
        
        # Header Row
        if show_headers:
            self.header_frame = tk.Frame(self, bg=CARD_BG, highlightbackground=BORDER_COLOR, highlightthickness=1)
            self.header_frame.pack(fill="x", pady=(0, 5))
            
            for col_idx, (col_name, weight) in enumerate(columns):
                self.header_frame.grid_columnconfigure(col_idx, weight=weight)
                lbl = tk.Label(self.header_frame, text=col_name, bg=CARD_BG, fg=TEXT_COLOR, 
                               font=FONT_BODY_BOLD, anchor="w", padx=10, pady=8)
                lbl.grid(row=0, column=col_idx, sticky="ew")
                
        # Scrollable rows frame
        self.scroll_frame = ScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True)
        
    def clear(self):
        for child in self.scroll_frame.scrollable_frame.winfo_children():
            child.destroy()
        self.rows = []
        
    def add_row(self, values, data=None, on_click=None):
        row_idx = len(self.rows)
        bg = CARD_BG if row_idx % 2 == 0 else BG_COLOR
        
        row_frame = tk.Frame(self.scroll_frame.scrollable_frame, bg=bg, highlightbackground=BORDER_COLOR, highlightthickness=1)
        row_frame.pack(fill="x", pady=2)
        
        for col_idx, (col_name, weight) in enumerate(self.columns):
            row_frame.grid_columnconfigure(col_idx, weight=weight)
            val = values[col_idx] if col_idx < len(values) else ""
            
            # Label with alignment
            lbl = tk.Label(row_frame, text=str(val), bg=bg, fg=TEXT_COLOR, 
                           font=FONT_BODY, anchor="w", padx=10, pady=8, wraplength=350)
            lbl.grid(row=0, column=col_idx, sticky="ew")
            
            # Bubble up click events
            if on_click:
                lbl.bind("<Button-1>", lambda e, d=data: on_click(d))
                lbl.configure(cursor="hand2")
                
        if on_click:
            row_frame.bind("<Button-1>", lambda e, d=data: on_click(d))
            row_frame.configure(cursor="hand2")
            
        self.rows.append((row_frame, data))
        return row_frame
