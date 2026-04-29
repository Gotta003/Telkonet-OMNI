import tkinter as tk
from tkinter import ttk

class NexusLightOS:
    def __init__(self, root):
        self.root = root
        self.root.title("NEXUS LIGHT - Smart Hospitality")
        
        # Fixed geometry with "x"
        self.root.geometry("1300x850")
        self.root.configure(bg="#f8fafc") 

        # State management
        self.device_states = {}
        self.current_overlay = None
        
        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Clean Modern Slider
        style.configure("Nexus.Horizontal.TScale", 
                        background="#ffffff", 
                        troughcolor="#e2e8f0", 
                        sliderthickness=20, 
                        borderwidth=0)
        
        style.map("Nexus.Horizontal.TScale",
                  background=[('pressed', '#3b82f6'), ('active', '#60a5fa')])

    def create_widgets(self):
        # --- MAIN VIEW ---
        self.main_content = tk.Frame(self.root, bg="#f8fafc")
        self.main_content.pack(side="right", fill="both", expand=True)

        # TOP BAR (Elegant Header)
        top_bar = tk.Frame(self.main_content, bg="#ffffff", pady=30, padx=50)
        top_bar.pack(fill="x")
        
        title_frame = tk.Frame(top_bar, bg="#ffffff")
        title_frame.pack(side="left")
        
        tk.Label(title_frame, text="Grand Imperial Suite", font=("Segoe UI", 28, "bold"), fg="#1e293b", bg="#ffffff").pack(anchor="w")
        tk.Label(title_frame, text="CONTROL PANEL • UNIT 404 • ONLINE", font=("Segoe UI", 10, "bold"), fg="#94a3b8", bg="#ffffff").pack(anchor="w", pady=2)

        # CANVAS AREA (The Blueprint)
        canvas_container = tk.Frame(self.main_content, bg="#f8fafc", padx=50, pady=30)
        canvas_container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(canvas_container, bg="#f8fafc", highlightthickness=0, bd=0)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        self.draw_master_plan()

    def draw_master_plan(self):
        # Room definitions with Pastel Colors
        rooms = [
            (50, 50, 450, 380, "MASTER SUITE", "#e0f2fe", "#0369a1"),   
            (470, 50, 800, 380, "GUEST ROOM A", "#dcfce7", "#15803d"),  
            (820, 50, 1150, 380, "GUEST ROOM B", "#fef3c7", "#b45309"), 
            (50, 410, 650, 750, "ROYAL LOUNGE", "#fae8ff", "#a21caf"),  
            (670, 410, 1150, 750, "DINING & KITCHEN", "#f1f5f9", "#475569"), 
        ]

        for x1, y1, x2, y2, name, color, accent in rooms:
            # Room Rectangle
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="#e2e8f0", width=2, fill=color)
            
            # Room Label
            self.canvas.create_text(x1+20, y1+25, text=name, anchor="w", fill=accent, font=("Segoe UI", 12, "bold"))
            
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            
            # Nodes with better alignment and English labels
            self.add_smart_node(mid_x - 80, mid_y, "💡", f"Lights - {name}", "DIMMER")
            self.add_smart_node(mid_x, mid_y, "🌡️", f"Climate - {name}", "TEMP")
            self.add_smart_node(mid_x + 80, mid_y, "🎵", f"Audio - {name}", "VOL")

    def add_smart_node(self, x, y, icon, name, type_key):
        # White background circle (button effect)
        # Using a slightly larger circle for better visual balance
        node = self.canvas.create_oval(x-28, y-28, x+28, y+28, fill="white", outline="#e2e8f0", width=1)
        
        # Centering adjustment: Some icons need a tiny offset to look centered
        # Especially the thermometer and music note which often lean one way
        offset_x, offset_y = 0, 0
        if icon == "🌡️": offset_x = 1 # Nudge thermometer right
        if icon == "🎵": offset_x = 2 # Nudge music note right
        
        txt = self.canvas.create_text(x + offset_x, y + offset_y, text=icon, fill="#1e293b", font=("Segoe UI Emoji", 18))
        
        def on_click(e): self.show_pro_overlay(x, y, name, type_key)
        
        # Hover events
        for item in [node, txt]:
            self.canvas.tag_bind(item, "<Button-1>", on_click)
            self.canvas.tag_bind(item, "<Enter>", lambda e: self.canvas.itemconfig(node, outline="#3b82f6", width=2))
            self.canvas.tag_bind(item, "<Leave>", lambda e: self.canvas.itemconfig(node, outline="#e2e8f0", width=1))

    def show_pro_overlay(self, x, y, dev_name, dev_type):
        if self.current_overlay: self.current_overlay.destroy()

        # White Card Overlay
        overlay = tk.Frame(self.canvas, bg="white", highlightbackground="#e2e8f0", highlightthickness=1)
        self.current_overlay = overlay
        
        # Auto-positioning the card
        overlay.place(x=x-100, y=y+40, width=250)

        # Card Header
        header = tk.Frame(overlay, bg="#f8fafc", padx=15, pady=10)
        header.pack(fill="x")
        tk.Label(header, text=dev_name.upper(), font=("Segoe UI", 8, "bold"), fg="#64748b", bg="#f8fafc").pack(anchor="w")

        # Card Body
        body = tk.Frame(overlay, bg="white", padx=20, pady=20)
        body.pack(fill="both")

        controls = {
            "DIMMER": ("Light Intensity", "Brightness Level"), 
            "VOL": ("Audio Volume", "Sound Level"), 
            "TEMP": ("Climate Control", "Target Temperature")
        }
        label, sub = controls.get(dev_type, ("Control", "Adjust"))
        
        tk.Label(body, text=label, fg="#1e293b", bg="white", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tk.Label(body, text=sub, fg="#94a3b8", bg="white", font=("Segoe UI", 8)).pack(anchor="w")
        
        val_slider = ttk.Scale(body, from_=0, to=100, orient="horizontal", style="Nexus.Horizontal.TScale")
        val_slider.set(self.device_states.get(dev_name, 50))
        val_slider.pack(fill="x", pady=15)

        # Confirm Button
        save_btn = tk.Button(body, text="CONFIRM SETTINGS", 
                             command=lambda: self.save_state(dev_name, val_slider, save_btn, overlay), 
                             bg="#3b82f6", fg="white", font=("Segoe UI", 9, "bold"), 
                             bd=0, pady=10, cursor="hand2", activebackground="#2563eb")
        save_btn.pack(fill="x", pady=(5, 5))
        
        tk.Button(body, text="Cancel", command=overlay.destroy, bg="white", 
                  fg="#94a3b8", font=("Segoe UI", 8), bd=0, cursor="hand2").pack(fill="x")

    def save_state(self, dev_name, slider, btn, overlay):
        self.device_states[dev_name] = int(slider.get())
        btn.config(text="✓ SAVED", bg="#10b981")
        self.root.after(500, lambda: overlay.destroy())

if __name__ == "__main__":
    root = tk.Tk()
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    app = NexusLightOS(root)
    root.mainloop()