import tkinter as tk
from tkinter import ttk
from datetime import datetime
import queue

# ================= ORIGINAL NETWORK INTEGRATION =================
try:
    import network_client as nc
    from constants import BRIDGE_URL, ROOM_ID_MAP, SUITES, ROOMS, UI_REFRESH_MS
    NETWORK_AVAILABLE = True
except ImportError:
    # Safe fallback configuration if local modules are missing
    BRIDGE_URL = "http://127.0.0.1:5000"
    SUITES = ["SUITE 1", "SUITE 2", "SUITE 3", "SUITE 4", "SUITE 5"]
    ROOMS = ["ENTRY", "HALL", "BATH", "BEDROOM", "EN-SUITE", "KITCHENETTE", "LIVING"]
    ROOM_ID_MAP = {
        "ENTRY": "entry", "HALL": "hall", "BATH": "bath", 
        "BEDROOM": "bedroom", "EN-SUITE": "ensuite", 
        "KITCHENETTE": "kitchen", "LIVING": "living"
    }
    UI_REFRESH_MS = 2000
    NETWORK_AVAILABLE = False


class NexusReceptionMonitor:

    def __init__(self, root):
        self.root = root
        self.root.title("TELKONET OMNIROOM - LUXURY RECEPTION MONITOR")
        self.root.geometry("1600x950")
        self.root.minsize(1400, 850)
        
        self.event_queue = queue.Queue()
        self.current_theme = "light"
        self.standby_mode = False
        
        self.selected_suite = tk.StringVar(value="SUITE 1")
        self.active_room = "ENTRY"

        # ================= STYLE TOKENS PARALLEL TO GUI-USER =================
        self.themes = {
            "light": {
                "bg": "#f4f2ee",
                "surface": "#ffffff",
                "surface_2": "#f9f8f6",
                "surface_3": "#f0ede8",
                "border": "#ddd9d2",
                "accent": "#c8973a",
                "accent_dim": "#a07828",
                "accent_soft": "#f5ece1",
                "text": "#0d1b2e",
                "text_dim": "#7a7060",
                "green": "#16a34a",
                "red": "#dc2626",
                "font_display": ("Playfair Display", 20, "bold"),
                "font_subtitle": ("Inter", 12, "bold"),
                "font_body": ("Inter", 11),
                "font_mono": ("JetBrains Mono", 10, "bold") # Ridotto leggermente per garantire spazio nei bottoni
            },
            "dark": {
                "bg": "#0d0e12",
                "surface": "#13151c",
                "surface_2": "#1a1d27",
                "surface_3": "#252838",
                "border": "#2a2e3f",
                "accent": "#e8a020",
                "accent_dim": "#7a5010",
                "accent_soft": "#2d261a",
                "text": "#e8eaf0",
                "text_dim": "#6b7280",
                "green": "#22c55e",
                "red": "#ef4444",
                "font_display": ("Rajdhani", 22, "bold"),
                "font_subtitle": ("Rajdhani", 14, "bold"),
                "font_body": ("Inter", 11),
                "font_mono": ("Share Tech Mono", 11, "bold")
            }
        }

        self.rooms_data = {}
        for suite in SUITES:
            for room in ROOMS:
                key = f"{suite} - {room}"
                self.rooms_data[key] = {
                    "lights": {"ceiling": 0, "floor": 0, "accent": 0, "reading": 0},
                    "climate": 21.5,
                    "humidity": 45,
                    "audio": 0,
                    "curtainOpen": False,
                    "active_scene": "Standard"
                }

        self.apply_theme_tokens()
        self.create_widgets()
        
        self.update_clock()
        self.process_network_queue()

        if NETWORK_AVAILABLE:
            nc.on("connect", lambda _: self.event_queue.put(("LOG", "SYSTEM", "Connected to Omniroom Bridge", "green")))
            nc.on("disconnect", lambda _: self.event_queue.put(("LOG", "SYSTEM", "Bridge communication lost", "red")))
            nc.on("button", lambda d: self.event_queue.put(("LOG", "GUEST", f"Physical Button Triggered: {d}", "accent")))
            nc.on("proximity", lambda d: self.event_queue.put(("PROXIMITY", d)))
            nc.on("command", lambda d: self.event_queue.put(("LOG", "ECHO", f"Command Received: {d}", "text")))
            nc.on("state_update", lambda state_data: self.event_queue.put(("STATE", state_data)))
            
            nc.start()
            self.poll_network_loop()

    def apply_theme_tokens(self):
        self.tokens = self.themes[self.current_theme]
        self.root.configure(bg=self.tokens["bg"])
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Luxury.TCombobox",
                        fieldbackground=self.tokens["surface"],
                        background=self.tokens["surface"],
                        foreground=self.tokens["accent"],
                        padding=4, # Ridotto per evitare il taglio verticale della scritta interna
                        relief="flat",
                        font=self.tokens["font_body"])

    def create_widgets(self):
        for w in self.root.winfo_children():
            w.destroy()

        if self.standby_mode:
            self.create_standby_screen()
            return

        # ---- TOP HEADER PANEL ----
        header = tk.Frame(self.root, bg=self.tokens["surface"], highlightbackground=self.tokens["border"], highlightthickness=1)
        header.pack(fill="x", padx=20, pady=(20, 10))

        tk.Label(header, text="TELKONET OMNIROOM", font=self.tokens["font_display"], bg=self.tokens["surface"], fg=self.tokens["accent"]).pack(side="left", padx=(20, 15), pady=12)
        tk.Label(header, text="•  Reception Data Monitor Console", font=self.tokens["font_body"], bg=self.tokens["surface"], fg=self.tokens["text_dim"]).pack(side="left", pady=18)

        theme_btn = tk.Button(header, text="SWITCH THEME", font=self.tokens["font_mono"], bg=self.tokens["surface_3"], fg=self.tokens["text"], relief="flat", bd=0, padx=15, pady=6, cursor="hand2", command=self.toggle_theme)
        theme_btn.pack(side="right", padx=20, pady=12)

        self.clock_lbl = tk.Label(header, font=self.tokens["font_mono"], bg=self.tokens["surface"], fg=self.tokens["text"])
        self.clock_lbl.pack(side="right", padx=10, pady=15)

        # ---- MAIN WRAPPER (Convertito a Grid Proporzionale) ----
        main_container = tk.Frame(self.root, bg=self.tokens["bg"])
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Definiamo le proporzioni: 25% Sinistra, 50% Centro, 25% Destra
        main_container.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=25, minsize=380) # Pannello Stanze
        main_container.columnconfigure(1, weight=50, minsize=640) # Pannello Centrale
        main_container.columnconfigure(2, weight=25, minsize=380) # Pannello Log

        # ---- PANEL LEFT: BLUEPRINT & SUITE SELECTION ----
        left_panel = tk.Frame(main_container, bg=self.tokens["surface"], highlightbackground=self.tokens["border"], highlightthickness=1)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        tk.Label(left_panel, text="SUITE SELECTION", font=self.tokens["font_subtitle"], bg=self.tokens["surface"], fg=self.tokens["accent_dim"]).pack(anchor="w", padx=20, pady=(20, 8))
        
        self.suite_menu = ttk.Combobox(left_panel, textvariable=self.selected_suite, values=SUITES, state="readonly", style="Luxury.TCombobox")
        self.suite_menu.pack(fill="x", padx=20, pady=5)
        self.suite_menu.bind("<<ComboboxSelected>>", self.change_suite)

        tk.Label(left_panel, text="FLOOR PLAN ROOMS", font=self.tokens["font_subtitle"], bg=self.tokens["surface"], fg=self.tokens["text_dim"]).pack(anchor="w", padx=20, pady=(25, 8))

        self.blueprint_frame = tk.Frame(left_panel, bg=self.tokens["surface_2"])
        self.blueprint_frame.pack(fill="both", expand=True, padx=20, pady=(5, 20))
        self.render_blueprint_rooms()

        # ---- PANEL CENTER: ROOM DETAIL PARAMS ----
        self.center_panel = tk.Frame(main_container, bg=self.tokens["surface"], highlightbackground=self.tokens["border"], highlightthickness=1)
        self.center_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 15))
        self.render_room_details_panel()

        # ---- PANEL RIGHT: REALTIME NOTIFICATION & ACTIVITY LOG ----
        right_panel = tk.Frame(main_container, bg=self.tokens["surface"], highlightbackground=self.tokens["border"], highlightthickness=1)
        right_panel.grid(row=0, column=2, sticky="nsew")

        tk.Label(right_panel, text="GUEST ACTIVITY LOG", font=self.tokens["font_subtitle"], bg=self.tokens["surface"], fg=self.tokens["text"]).pack(anchor="w", padx=20, pady=(20, 10))

        # width=10 costringe il widget a non forzare la larghezza della colonna grid oltre il consentito
        self.log_widget = tk.Text(right_panel, bg=self.tokens["surface_2"], fg=self.tokens["text"], font=self.tokens["font_mono"], state="disabled", borderwidth=0, padx=12, pady=12, wrap="word", width=10)
        self.log_widget.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.update_display_values()

    def render_blueprint_rooms(self):
        for w in self.blueprint_frame.winfo_children():
            w.destroy()

        for room in ROOMS:
            is_selected = (room == self.active_room)
            bg = self.tokens["accent_soft"] if is_selected else self.tokens["surface_3"]
            fg = self.tokens["accent_dim"] if is_selected else self.tokens["text"]
            bd = 1 if is_selected else 0

            btn = tk.Button(self.blueprint_frame, text=f"{room}  [ LIVE VIEW ]", font=self.tokens["font_mono"],
                            bg=bg, fg=fg, relief="solid", bd=bd, highlightthickness=0,
                            activebackground=self.tokens["accent_soft"], cursor="hand2", anchor="w", padx=10)
            btn.config(command=lambda r=room: self.select_room(r))
            btn.pack(fill="x", padx=10, pady=4, ipady=6)

    def render_room_details_panel(self):
        for w in self.center_panel.winfo_children():
            w.destroy()

        # Header Block
        header_block = tk.Frame(self.center_panel, bg=self.tokens["surface"])
        header_block.pack(fill="x", padx=30, pady=(25, 10))

        self.title_lbl = tk.Label(header_block, text="", font=self.tokens["font_display"], bg=self.tokens["surface"], fg=self.tokens["text"])
        self.title_lbl.pack(side="left", anchor="w")

        self.scene_badge = tk.Label(header_block, text="ACTIVE SCENE: --", font=self.tokens["font_mono"], bg=self.tokens["accent_soft"], fg=self.tokens["accent_dim"], padx=14, pady=5)
        self.scene_badge.pack(side="right", anchor="e")

        sep = tk.Frame(self.center_panel, height=1, bg=self.tokens["border"])
        sep.pack(fill="x", padx=30, pady=(5, 20))

        content_wrapper = tk.Frame(self.center_panel, bg=self.tokens["surface"])
        content_wrapper.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        content_wrapper.columnconfigure(0, weight=1)
        content_wrapper.columnconfigure(1, weight=0)

        self.display_labels = {}
        
        monitored_items = [
            ("Ambient Temperature Sensor", "climate", "°C"),
            ("Relative Humidity Sensor", "humidity", "%"),
            ("Room Audio Volume Level", "audio", "%"),
            ("Motorized Blinds Position", "curtainOpen", ""),
            ("Ceiling Light Intensity", "light_ceiling", "%"),
            ("Floor Lamp Intensity", "light_floor", "%"),
            ("Accent Light Strip Intensity", "light_accent", "%"),
            ("Reading Light Intensity", "light_reading", "%")
        ]

        for idx, (label_text, key, unit) in enumerate(monitored_items):
            content_wrapper.rowconfigure(idx, weight=1)

            lbl = tk.Label(content_wrapper, text=label_text, font=self.tokens["font_body"], bg=self.tokens["surface"], fg=self.tokens["text_dim"])
            lbl.grid(row=idx, column=0, sticky="w", pady=4)

            val_box = tk.Label(content_wrapper, text="--", font=self.tokens["font_mono"], bg=self.tokens["surface_2"], fg=self.tokens["accent"], width=18, relief="flat")
            val_box.grid(row=idx, column=1, sticky="e", padx=(20, 0), ipady=8) 
            
            self.display_labels[key] = (val_box, unit)

    def create_standby_screen(self):
        self.root.configure(bg="#05070a")
        box = tk.Frame(self.root, bg="#05070a")
        box.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(box, text="MONITOR STANDBY ACTIVE", font=("Rajdhani", 32, "bold"), bg="#05070a", fg="#3a4454").pack(pady=10)
        self.standby_clock = tk.Label(box, text="--:--:--", font=("Share Tech Mono", 56, "bold"), bg="#05070a", fg="#e8a020")
        self.standby_clock.pack(pady=5)
        tk.Label(box, text="No motion detected in suite • Console operating in energy saving mode", font=("Inter", 12), bg="#05070a", fg="#5a6474").pack(pady=10)

    # ================= REFRESH AND ACTION LOGIC =================
    def change_suite(self, event=None):
        self.add_log("RECEPTION", f"Active monitoring viewport shifted to {self.selected_suite.get()}", "text")
        self.update_display_values()

    def select_room(self, room):
        self.active_room = room
        self.render_blueprint_rooms()
        self.update_display_values()

    def update_display_values(self):
        if self.standby_mode: return
        
        suite = self.selected_suite.get()
        key = f"{suite} - {self.active_room}"
        data = self.rooms_data[key]

        self.title_lbl.config(text=f"{suite}  •  {self.active_room}")
        self.scene_badge.config(text=f"ACTIVE SCENE: {data['active_scene'].upper()}")

        self._set_lbl_data("climate", data["climate"])
        self._set_lbl_data("humidity", data["humidity"])
        self._set_lbl_data("audio", data["audio"])
        
        txt_curtain = "OPEN (100%)" if data["curtainOpen"] else "CLOSED (0%)"
        self._set_lbl_data("curtainOpen", txt_curtain)

        self._set_lbl_data("light_ceiling", data["lights"]["ceiling"])
        self._set_lbl_data("light_floor", data["lights"]["floor"])
        self._set_lbl_data("light_accent", data["lights"]["accent"])
        self._set_lbl_data("light_reading", data["lights"]["reading"])

    def _set_lbl_data(self, key, val):
        if key in self.display_labels:
            lbl, unit = self.display_labels[key]
            lbl.config(text=f"{val} {unit}".strip())

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme_tokens()
        self.create_widgets()

    # ================= THREAD-SAFE QUEUE MANAGER =================
    def process_network_queue(self):
        while not self.event_queue.empty():
            item = self.event_queue.get()
            evt_type = item[0]
            
            if evt_type == "LOG":
                self.add_log(item[1], item[2], item[3])
            elif evt_type == "PROXIMITY":
                should_standby = (item[1] == "sleep")
                if should_standby != self.standby_mode:
                    self.standby_mode = should_standby
                    self.apply_theme_tokens()
                    self.create_widgets()
            elif evt_type == "STATE":
                self.sync_with_server_state(item[1])
                
        self.root.after(150, self.process_network_queue)

    def sync_with_server_state(self, state):
        if not state: return
        suite = self.selected_suite.get()
        
        room_id = ROOM_ID_MAP.get(self.active_room, "entry")
        target_key = f"{suite} - {self.active_room}"
        
        net_lights = state.get("lights", {}).get(room_id, {})
        if net_lights:
            self.rooms_data[target_key]["lights"]["ceiling"] = net_lights.get("ceiling", 0)
            self.rooms_data[target_key]["lights"]["floor"] = net_lights.get("floor", 0)
            self.rooms_data[target_key]["lights"]["accent"] = net_lights.get("accent", 0)
            self.rooms_data[target_key]["lights"]["reading"] = net_lights.get("reading", 0)

        sensors = state.get("sensors", {})
        if sensors:
            self.rooms_data[target_key]["climate"] = sensors.get("temperature", 21.5)
            self.rooms_data[target_key]["humidity"] = sensors.get("humidity", 45)
            
        self.rooms_data[target_key]["curtainOpen"] = state.get("curtainOpen", False)
        
        self.update_display_values()

    def poll_network_loop(self):
        if NETWORK_AVAILABLE:
            self.sync_with_server_state(nc.get_state())
        self.root.after(UI_REFRESH_MS, self.poll_network_loop)

    # ================= UTILS & CLOCK =================
    def update_clock(self):
        time_str = datetime.now().strftime("%d/%m/%Y  %H:%M:%S")
        if not self.standby_mode:
            if hasattr(self, 'clock_lbl'): self.clock_lbl.config(text=time_str)
        else:
            if hasattr(self, 'standby_clock'): self.standby_clock.config(text=datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self.update_clock)

    def add_log(self, src, msg, color_token):
        if self.standby_mode: return
        self.log_widget.config(state="normal")
        
        color_hex = self.tokens.get(color_token, self.tokens["text"])
        tag_name = f"tag_{datetime.now().timestamp()}"
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        line = f"[{timestamp}] {src}: {msg}\n"
        
        self.log_widget.insert("end", line, tag_name)
        self.log_widget.tag_config(tag_name, foreground=color_hex)
        self.log_widget.see("end")
        self.root.update_idletasks()
        self.log_widget.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = NexusReceptionMonitor(root)
    root.mainloop()