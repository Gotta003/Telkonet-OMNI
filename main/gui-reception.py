import tkinter as tk
from tkinter import ttk
from datetime import datetime

class NexusReceptionMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("NEXUS LIGHT OS - RECEPTION MONITORING SYSTEM")
        self.root.geometry("1400x900")
        self.root.configure(bg="#F8FAFC") # Light background (Slate 50)

        # Configuration (Matching your HTML structure)
        self.rooms_config = [
            {"name": "ENTRY", "icon": "🔑"},
            {"name": "HALL", "icon": "🚪"},
            {"name": "LIVING", "icon": "🛋️"},
            {"name": "KITCHEN", "icon": "🍳"},
            {"name": "BEDROOM 1", "icon": "🛏️"},
            {"name": "BEDROOM 2", "icon": "🛌"},
            {"name": "BATH 1", "icon": "🚿"},
            {"name": "BATH 2", "icon": "🛁"},
            {"name": "UTILITY", "icon": "🧺"}         
        ]

        self.sensors = [
            {"name": "LIGHT", "icon": "💡"},
            {"name": "CLIMATE", "icon": "🌡️"},
            {"name": "MUSIC", "icon": "🎵"},
            {"name": "WINDOWS", "icon": "🪟"}
        ]

        # Mock Data (Reception only visualizes what comes from the "system")
        self.rooms_data = {r["name"]: {s["name"]: 50 for s in self.sensors} for r in self.rooms_config}
        self.current_room = "LIVING"

        self.create_widgets()
        self.select_room("LIVING")

    def create_widgets(self):
        # --- LEFT SIDEBAR (LARGE LIST) ---
        self.sidebar = tk.Frame(self.root, bg="#FFFFFF", width=350, highlightbackground="#E2E8F0", highlightthickness=1)
        self.sidebar.pack(side="left", fill="y")
        
        tk.Label(self.sidebar, text="SYSTEM ROOMS", font=("Segoe UI", 20, "bold"), 
                 bg="#FFFFFF", fg="#1E293B", pady=30).pack()

        for room in self.rooms_config:
            btn = tk.Button(self.sidebar, 
                            text=f"{room['icon']}  {room['name']}", 
                            command=lambda r=room['name']: self.select_room(r),
                            bg="#F1F5F9", fg="#334155", font=("Segoe UI", 14, "bold"),
                            relief="flat", activebackground="#2563EB", 
                            activeforeground="white", anchor="w", padx=30, pady=15, cursor="hand2")
            btn.pack(pady=5, padx=20, fill="x")

        # --- CENTRAL MONITORING PANEL ---
        self.main_panel = tk.Frame(self.root, bg="#F8FAFC")
        self.main_panel.pack(side="left", fill="both", expand=True, padx=60)

        # Room Status Header
        header_container = tk.Frame(self.main_panel, bg="#F8FAFC")
        header_container.pack(fill="x", pady=(50, 40))

        self.title_lbl = tk.Label(header_container, text=self.current_room, 
                                 font=("Segoe UI", 48, "bold"), bg="#F8FAFC", fg="#0F172A")
        self.title_lbl.pack(side="left")

        tk.Label(header_container, text=" LIVE STATUS", font=("Segoe UI", 16), 
                 bg="#F8FAFC", fg="#10B981").pack(side="left", padx=20, pady=(20, 0))

        # Data Display Cards
        self.display_elements = {}
        for sensor in self.sensors:
            s_name = sensor["name"]
            s_icon = sensor["icon"]

            # Large Card for each parameter
            card = tk.Frame(self.main_panel, bg="#FFFFFF", pady=30, padx=40, 
                            highlightbackground="#E2E8F0", highlightthickness=1)
            card.pack(fill="x", pady=15)

            # Labels
            tk.Label(card, text=f"{s_icon} {s_name}", font=("Segoe UI", 18, "bold"), 
                     bg="#FFFFFF", fg="#64748B").pack(side="left")
            
            val_lbl = tk.Label(card, text="50%", font=("Segoe UI", 24, "bold"), 
                              bg="#FFFFFF", fg="#2563EB")
            val_lbl.pack(side="right")

            # Progress Bar (Replaces Sliders to prevent manual editing)
            style = ttk.Style()
            style.configure("TProgressbar", thickness=20)
            
            pb = ttk.Progressbar(card, orient="horizontal", length=400, mode="determinate")
            pb.pack(side="right", padx=50)
            pb['value'] = 50
            
            self.display_elements[s_name] = {"bar": pb, "lbl": val_lbl}

        # --- RIGHT LOG PANEL (HUGE) ---
        self.log_frame = tk.Frame(self.root, bg="#1E293B", width=400)
        self.log_frame.pack(side="right", fill="y")
        
        tk.Label(self.log_frame, text="GLOBAL ACTIVITY LOG", font=("Segoe UI", 14, "bold"), 
                 bg="#1E293B", fg="#F8FAFC", pady=25).pack()

        self.log_box = tk.Text(self.log_frame, width=40, bg="#0F172A", fg="#38BDF8", 
                               font=("Consolas", 12), state="disabled", borderwidth=0, padx=20)
        self.log_box.pack(fill="both", expand=True, padx=15, pady=15)

    def select_room(self, name):
        self.current_room = name
        self.title_lbl.configure(text=name)
        
        # Visualize stored data
        data = self.rooms_data[name]
        for s_name, value in data.items():
            self.display_elements[s_name]["bar"]['value'] = value
            self.display_elements[s_name]["lbl"].configure(text=f"{value}%")
        
        self.add_log("RECEPTION", f"Authorized Access to {name} monitoring")

    def add_log(self, src, msg):
        time = datetime.now().strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{time}] {src}:\n> {msg}\n\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = NexusReceptionMonitor(root)
    root.mainloop()