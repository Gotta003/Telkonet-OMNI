import customtkinter as ctk
from datetime import datetime

# Theme Settings: Light mode with professional accents
ctk.set_appearance_mode("Light") 
ctk.set_default_color_theme("blue")

class ReceptionMonitor(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("OMNI SYSTEM - ROOM MONITORING DASHBOARD")
        self.geometry("1200x800")
        self.configure(fg_color="#f0f2f5") # Clean, modern gray-white

        # --- Header ---
        self.header = ctk.CTkLabel(self, text="HOSPITALITY CONTROL CENTER", 
                                   font=ctk.CTkFont(size=32, weight="bold"), text_color="#1c1e21")
        self.header.pack(pady=30)

        # --- Main Layout Container ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # --- LEFT PANEL: ROOMS (Grid) ---
        self.rooms_grid = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.rooms_grid.pack(side="left", fill="both", expand=True)
        self.rooms_grid.grid_columnconfigure((0, 1), weight=1)
        self.rooms_grid.grid_rowconfigure(0, weight=1)

        self.create_room_card(self.rooms_grid, "SUITE 101", 0, "OCCUPIED", "#e74c3c")
        self.create_room_card(self.rooms_grid, "ROOM 102", 1, "AVAILABLE", "#2ecc71")

        # --- RIGHT PANEL: LOGS ---
        self.sidebar = ctk.CTkFrame(self.main_container, width=350, corner_radius=20, fg_color="#ffffff", border_width=1, border_color="#dce0e4")
        self.sidebar.pack(side="right", fill="y", padx=(20, 0))
        self.sidebar.pack_propagate(False)
        
        ctk.CTkLabel(self.sidebar, text="SYSTEM LOGS", font=ctk.CTkFont(size=18, weight="bold"), text_color="#606770").pack(pady=20)
        
        self.log_box = ctk.CTkTextbox(self.sidebar, font=("Consolas", 12), fg_color="#f5f6f7", 
                                      text_color="#1c1e21", border_width=0)
        self.log_box.pack(padx=20, pady=10, fill="both", expand=True)
        self.log_box.configure(state="disabled")

        self.add_log("System", "Monitoring service active")

    def create_room_card(self, parent, name, col, status, status_color):
        # Professional Card
        card = ctk.CTkFrame(parent, corner_radius=25, fg_color="#ffffff", border_width=1, border_color="#dce0e4")
        card.grid(row=0, column=col, padx=15, pady=10, sticky="nsew")

        # Room Name & Status Badge
        ctk.CTkLabel(card, text=name, font=ctk.CTkFont(size=28, weight="bold"), text_color="#1c1e21").pack(pady=(25, 5))
        
        status_badge = ctk.CTkLabel(card, text=f" {status} ", font=ctk.CTkFont(size=14, weight="bold"), 
                                    text_color="#ffffff", fg_color=status_color, corner_radius=10)
        status_badge.pack(pady=(0, 20))

        # Large Sensor Metrics
        sensor_frame = ctk.CTkFrame(card, fg_color="#f8f9fa", corner_radius=15)
        sensor_frame.pack(padx=25, fill="x", pady=10)
        
        metrics = [("🌡️", "23.5°C", "TEMP"), ("💧", "48%", "HUMIDITY"), ("☀️", "150lx", "LIGHT")]
        for icon, m_val, m_name in metrics:
            f = ctk.CTkFrame(sensor_frame, fg_color="transparent")
            f.pack(side="left", expand=True, pady=15)
            ctk.CTkLabel(f, text=icon, font=ctk.CTkFont(size=24)).pack()
            ctk.CTkLabel(f, text=m_val, font=ctk.CTkFont(size=18, weight="bold"), text_color="#1c1e21").pack()
            ctk.CTkLabel(f, text=m_name, font=ctk.CTkFont(size=11), text_color="#8d949e").pack()

        # Display-only Progress Bars (HVAC & Shades)
        self.create_read_only_bar(card, "CLIMATE CONTROL", 0.75, "75% Power Output")
        self.create_read_only_bar(card, "SMART SHADES", 1.0, "Fully Opened")

        # Status Indicators (Large Icons)
        status_row = ctk.CTkFrame(card, fg_color="transparent")
        status_row.pack(side="bottom", fill="x", pady=30, padx=20)

        self.create_status_icon(status_row, "💡", "L1", True)
        self.create_status_icon(status_row, "💡", "L2", False)
        self.create_status_icon(status_row, "🔊", "AUDIO", False)

    def create_read_only_bar(self, parent, label, value, detail):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=40, pady=12)
        
        ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=13, weight="bold"), text_color="#444").pack(anchor="w")
        bar = ctk.CTkProgressBar(frame, height=15, corner_radius=10)
        bar.set(value)
        bar.pack(fill="x", pady=5)
        ctk.CTkLabel(frame, text=detail, font=ctk.CTkFont(size=11), text_color="#888").pack(anchor="e")

    def create_status_icon(self, parent, icon, label, is_active):
        frame = ctk.CTkFrame(parent, fg_color="#f0f2f5" if is_active else "#f9f9f9", corner_radius=12, width=90)
        frame.pack(side="left", expand=True, padx=8, pady=5)
        
        color = "#3498db" if is_active else "#bcc0c4"
        bg_circle = "#e7f3ff" if is_active else "#f0f2f5"
        
        icon_lbl = ctk.CTkLabel(frame, text=icon, font=ctk.CTkFont(size=26), text_color=color)
        icon_lbl.pack(pady=(10, 0))
        
        text_st = "ACTIVE" if is_active else "OFF"
        ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=11, weight="bold"), text_color="#606770").pack()
        ctk.CTkLabel(frame, text=text_st, font=ctk.CTkFont(size=10, weight="bold"), text_color=color).pack(pady=(0, 10))

    def add_log(self, source, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {source.upper()}: {message}\n"
        self.log_box.configure(state="normal")
        self.log_box.insert("end", log_entry)
        self.log_box.configure(state="disabled")
        self.log_box.see("end")

if __name__ == "__main__":
    app = ReceptionMonitor()
    app.mainloop()