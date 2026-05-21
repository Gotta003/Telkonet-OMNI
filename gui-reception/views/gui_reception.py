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
        self.standby_mode = False
        
        # --- GESTIONE TIMER STANDBY PER INATTIVITÀ ---
        self.standby_timeout_ms = 30000  # 30 secondi di inattività
        self.standby_timer_id = None      
        
        self.selected_suite = tk.StringVar(value="SUITE 1")
        self.active_room = "ENTRY"

        # ================= APP GRAPHICAL SETTINGS STATE =================
        self.settings = {
            "theme": "light",              
            "accent": "#c8973a",           
            "font_size": 16,               
            "font_style": "Modern",        
            "fixture_size": "Medium",      
            "room_fill": "Neutral",        
            "clock_format": "24h",         
            "show_seconds": True,          
            "animation_speed": "Fast"      
        }
        self.view_mode = "details"         

        self.accent_palette = [
            {"hex": "#c8973a", "name": "Gold"},
            {"hex": "#b45309", "name": "Rust"},
            {"hex": "#15803d", "name": "Green"},
            {"hex": "#1d4ed8", "name": "Blue"},
            {"hex": "#6d28d9", "name": "Purple"},
            {"hex": "#374151", "name": "Dark Grey"}
        ]

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
                "red": "#dc2626"
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
                "red": "#ef4444"
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

        # Attiva i binding globali e avvia il primo timer
        self.setup_activity_bindings()
        self.reset_standby_timer()

        if NETWORK_AVAILABLE:
            nc.on("connect", lambda _: self.event_queue.put(("LOG", "SYSTEM", "Connected to Omniroom Bridge", "green")))
            nc.on("disconnect", lambda _: self.event_queue.put(("LOG", "SYSTEM", "Bridge communication lost", "red")))
            nc.on("button", lambda d: self.event_queue.put(("LOG", "GUEST", f"Physical Button Triggered: {d}", "accent")))
            nc.on("proximity", lambda d: self.event_queue.put(("PROXIMITY", d)))
            nc.on("command", lambda d: self.event_queue.put(("LOG", "ECHO", f"Command Received: {d}", "text")))
            nc.on("state_update", lambda state_data: self.event_queue.put(("STATE", state_data)))
            
            nc.start()
            self.poll_network_loop()

    # ================= LOGICA DI ATTIVITÀ / INATTIVITÀ (CORRETTA) =================
    def setup_activity_bindings(self):
        """Assegna gli eventi di input alla finestra principale."""
        self.root.bind_all("<Any-KeyPress>", self.on_user_activity)
        self.root.bind_all("<Motion>", self.on_user_activity)
        self.root.bind_all("<Button-1>", self.on_user_activity)

    def on_user_activity(self, event=None):
        """Eseguito ad ogni interazione dell'utente sulla console."""
        if self.standby_mode:
            # SVEGLIA LA CONSOLE: Cambiamo lo stato PRIMA di ricostruire la GUI
            self.standby_mode = False
            self.apply_theme_tokens()
            self.create_widgets()
            self.add_log("SYSTEM", "Console awakened by local user activity", "green")
        
        # Resetta sempre il countdown per lo standby
        self.reset_standby_timer()

    def reset_standby_timer(self):
        """Azzera il vecchio timer e ne crea uno nuovo da 30 secondi."""
        if self.standby_timer_id is not None:
            self.root.after_cancel(self.standby_timer_id)
            self.standby_timer_id = None
        
        # Crea il timer solo se lo schermo è attivo
        if not self.standby_mode:
            self.standby_timer_id = self.root.after(self.standby_timeout_ms, self.trigger_standby)

    def trigger_standby(self):
        """Entra in modalità standby dopo 30s di inattività totale."""
        if not self.standby_mode:
            self.standby_mode = True
            if self.standby_timer_id is not None:
                self.root.after_cancel(self.standby_timer_id)
                self.standby_timer_id = None
                
            self.apply_theme_tokens()
            self.create_widgets()

    # ================= INTERFACCIA GRAFICA E LOGICA BASE =================
    def apply_theme_tokens(self):
        selected_theme = str(self.settings["theme"]).lower()
        if selected_theme == "auto":
            hour = datetime.now().hour
            theme_key = "dark" if (hour < 7 or hour > 19) else "light"
        else:
            theme_key = selected_theme

        self.tokens = self.themes[theme_key].copy()
        self.tokens["accent"] = self.settings["accent"]
        
        base_sz = self.settings["font_size"]
        style_type = self.settings["font_style"]
        
        if style_type == "Modern":
            font_family = "Inter"
        elif style_type == "Classic":
            font_family = "Playfair Display"
        else:
            font_family = "JetBrains Mono"

        self.tokens["font_display"] = (font_family, int(base_sz * 1.3), "bold")
        self.tokens["font_subtitle"] = (font_family, int(base_sz * 0.85), "bold")
        self.tokens["font_body"] = (font_family, int(base_sz * 0.75))
        self.tokens["font_mono"] = ("JetBrains Mono" if style_type == "Mono" else "Courier", int(base_sz * 0.7), "bold")
        
        self.root.configure(bg=self.tokens["bg"])
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Luxury.TCombobox",
                        fieldbackground=self.tokens["surface"],
                        background=self.tokens["surface"],
                        foreground=self.tokens["accent"],
                        padding=4,
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

        btn_text = "BACK TO MONITOR" if self.view_mode == "settings" else "⚙ SYSTEM SETTINGS"
        view_btn = tk.Button(header, text=btn_text, font=self.tokens["font_mono"], bg=self.tokens["surface_3"], fg=self.tokens["text"], relief="flat", bd=0, padx=15, pady=6, cursor="hand2", command=self.toggle_view_mode)
        view_btn.pack(side="right", padx=20, pady=12)

        self.clock_lbl = tk.Label(header, font=self.tokens["font_mono"], bg=self.tokens["surface"], fg=self.tokens["text"])
        self.clock_lbl.pack(side="right", padx=10, pady=15)

        # ---- MAIN WRAPPER ----
        main_container = tk.Frame(self.root, bg=self.tokens["bg"])
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        main_container.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=25, minsize=380) 
        main_container.columnconfigure(1, weight=50, minsize=640) 
        main_container.columnconfigure(2, weight=25, minsize=380) 

        # ---- PANEL LEFT ----
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

        # ---- PANEL CENTER ----
        self.center_panel = tk.Frame(main_container, bg=self.tokens["surface"], highlightbackground=self.tokens["border"], highlightthickness=1)
        self.center_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 15))
        
        if self.view_mode == "settings":
            self.render_settings_panel()
        else:
            self.render_room_details_panel()

        # ---- PANEL RIGHT ----
        right_panel = tk.Frame(main_container, bg=self.tokens["surface"], highlightbackground=self.tokens["border"], highlightthickness=1)
        right_panel.grid(row=0, column=2, sticky="nsew")

        tk.Label(right_panel, text="GUEST ACTIVITY LOG", font=self.tokens["font_subtitle"], bg=self.tokens["surface"], fg=self.tokens["text"]).pack(anchor="w", padx=20, pady=(20, 10))

        self.log_widget = tk.Text(right_panel, bg=self.tokens["surface_2"], fg=self.tokens["text"], font=self.tokens["font_mono"], state="disabled", borderwidth=0, padx=12, pady=12, wrap="word", width=10)
        self.log_widget.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        if self.view_mode == "details":
            self.update_display_values()

    def toggle_view_mode(self):
        self.view_mode = "details" if self.view_mode == "settings" else "settings"
        self.create_widgets()

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

    def render_settings_panel(self):
        for w in self.center_panel.winfo_children():
            w.destroy()

        title_frame = tk.Frame(self.center_panel, bg=self.tokens["surface"])
        title_frame.pack(fill="x", padx=30, pady=(25, 15))
        tk.Label(title_frame, text="CONSOLE SETTINGS", font=self.tokens["font_display"], bg=self.tokens["surface"], fg=self.tokens["text"]).pack(side="left")

        scroll_box = tk.Frame(self.center_panel, bg=self.tokens["surface"])
        scroll_box.pack(fill="both", expand=True, padx=30, pady=5)

        self.build_section_header(scroll_box, "APPEARANCE")
        self.build_segmented_row(scroll_box, "Theme", "Choose between light and dark mode", 
                                 ["Light", "Dark", "Auto"], str(self.settings["theme"]).capitalize(), 
                                 lambda v: self.update_setting("theme", str(v).lower()))
        self.build_accent_picker_row(scroll_box)

        self.build_section_header(scroll_box, "TYPOGRAPHY")
        self.build_slider_row(scroll_box, "Font size", "Base size for all text - larger helps readability", 
                              12, 24, self.settings["font_size"], 
                              lambda v: self.update_setting("font_size", int(float(v))))
        self.build_segmented_row(scroll_box, "Font Style", "Interface typeface", 
                                 ["Modern", "Classic", "Mono"], self.settings["font_style"], 
                                 lambda v: self.update_setting("font_style", v))

        self.build_section_header(scroll_box, "FLOOR PLAN")
        self.build_segmented_row(scroll_box, "Fixture icon size", "Size of light fixture markers on the plan", 
                                 ["Small", "Medium", "Large"], self.settings["fixture_size"], 
                                 lambda v: self.update_setting("fixture_size", v))
        self.build_segmented_row(scroll_box, "Room Fill Style", "How lit rooms are shown on the plan", 
                                 ["Warm", "Neutral", "Minimal"], self.settings["room_fill"], 
                                 lambda v: self.update_setting("room_fill", v))

        self.build_section_header(scroll_box, "CLOCK & STATUS")
        self.build_segmented_row(scroll_box, "Clock format", "How the time is shown in header", 
                                 ["24h", "12h"], self.settings["clock_format"], 
                                 lambda v: self.update_setting("clock_format", v))
        self.build_segmented_row(scroll_box, "Show seconds", "Display seconds in the clock", 
                                 ["On", "Off"], "On" if self.settings["show_seconds"] else "Off", 
                                 lambda v: self.update_setting("show_seconds", v == "On"))

        self.build_section_header(scroll_box, "INTERACTION")
        self.build_segmented_row(scroll_box, "Panel animation speed", "How fast the right panel slides in and out", 
                                 ["None", "Fast", "Slow"], self.settings["animation_speed"], 
                                 lambda v: self.update_setting("animation_speed", v))

    def build_section_header(self, parent, text):
        f = tk.Frame(parent, bg=self.tokens["surface"])
        f.pack(fill="x", pady=(20, 5))
        tk.Label(f, text=text, font=self.tokens["font_mono"], fg=self.tokens["text_dim"], bg=self.tokens["surface"]).pack(side="left")
        sep = tk.Frame(parent, height=1, bg=self.tokens["border"])
        sep.pack(fill="x", pady=(2, 10))

    def build_segmented_row(self, parent, title, subtitle, options, current_val, callback):
        row = tk.Frame(parent, bg=self.tokens["surface"])
        row.pack(fill="x", pady=6)
        
        desc_frame = tk.Frame(row, bg=self.tokens["surface"])
        desc_frame.pack(side="left", fill="both")
        tk.Label(desc_frame, text=title, font=self.tokens["font_subtitle"], fg=self.tokens["text"], bg=self.tokens["surface"]).pack(anchor="w")
        tk.Label(desc_frame, text=subtitle, font=self.tokens["font_body"], fg=self.tokens["text_dim"], bg=self.tokens["surface"]).pack(anchor="w")

        btn_container = tk.Frame(row, bg=self.tokens["border"], bd=1)
        btn_container.pack(side="right", anchor="center")

        for opt in options:
            active = (str(opt).lower() == str(current_val).lower())
            bg = self.tokens["surface"] if not active else self.tokens["accent_soft"]
            fg = self.tokens["text"] if not active else self.tokens["accent"]
            
            btn = tk.Button(btn_container, text=str(opt), font=self.tokens["font_body"], bg=bg, fg=fg,
                            relief="flat", bd=0, padx=14, pady=6, cursor="hand2",
                            command=lambda o=opt: callback(o))
            btn.pack(side="left", padx=1)

    def build_slider_row(self, parent, title, subtitle, min_v, max_v, current_val, callback):
        row = tk.Frame(parent, bg=self.tokens["surface"])
        row.pack(fill="x", pady=6)

        desc_frame = tk.Frame(row, bg=self.tokens["surface"])
        desc_frame.pack(side="left", fill="both")
        tk.Label(desc_frame, text=title, font=self.tokens["font_subtitle"], fg=self.tokens["text"], bg=self.tokens["surface"]).pack(anchor="w")
        tk.Label(desc_frame, text=subtitle, font=self.tokens["font_body"], fg=self.tokens["text_dim"], bg=self.tokens["surface"]).pack(anchor="w")

        ctrl_frame = tk.Frame(row, bg=self.tokens["surface"])
        ctrl_frame.pack(side="right", fill="y")

        val_lbl = tk.Label(ctrl_frame, text=f"{current_val}px", font=self.tokens["font_mono"], fg=self.tokens["accent"], bg=self.tokens["surface"], width=6)
        val_lbl.pack(side="right", padx=(10, 0))

        slider = ttk.Scale(ctrl_frame, from_=min_v, to=max_v, value=current_val, command=callback, length=150)
        slider.pack(side="right", anchor="center")

    def build_accent_picker_row(self, parent):
        row = tk.Frame(parent, bg=self.tokens["surface"])
        row.pack(fill="x", pady=6)

        desc_frame = tk.Frame(row, bg=self.tokens["surface"])
        desc_frame.pack(side="left", fill="both")
        tk.Label(desc_frame, text="Accent colour", font=self.tokens["font_subtitle"], fg=self.tokens["text"], bg=self.tokens["surface"]).pack(anchor="w")
        tk.Label(desc_frame, text="Highlight colour used throughout the interface", font=self.tokens["font_body"], fg=self.tokens["text_dim"], bg=self.tokens["surface"]).pack(anchor="w")

        picker_frame = tk.Frame(row, bg=self.tokens["surface"])
        picker_frame.pack(side="right", anchor="center")

        for color in self.accent_palette:
            is_selected = (self.settings["accent"] == color["hex"])
            border_color = self.tokens["text"] if is_selected else self.tokens["surface"]
            
            outer_ring = tk.Frame(picker_frame, bg=border_color, padding=2, bd=2 if is_selected else 0)
            outer_ring.pack(side="left", padx=4)

            btn = tk.Button(outer_ring, bg=color["hex"], width=3, height=1, relief="flat", cursor="hand2",
                            command=lambda c=color["hex"]: self.update_setting("accent", c))
            btn.pack()

    def update_setting(self, key, value):
        self.settings[key] = value
        self.apply_theme_tokens()
        self.create_widgets()

    def render_room_details_panel(self):
        for w in self.center_panel.winfo_children():
            w.destroy()

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
        tk.Label(box, text="Console operating in energy saving mode • Move mouse or type to awake", font=("Inter", 12), bg="#05070a", fg="#5a6474").pack(pady=10)

    def change_suite(self, event=None):
        self.add_log("RECEPTION", f"Active monitoring viewport shifted to {self.selected_suite.get()}", "text")
        if self.view_mode == "details":
            self.update_display_values()

    def select_room(self, room):
        self.active_room = room
        self.render_blueprint_rooms()
        if self.view_mode == "details":
            self.update_display_values()

    def update_display_values(self):
        if self.standby_mode or self.view_mode == "settings": return
        
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

    def update_clock(self):
        time_format = "%d/%m/%Y  "
        if self.settings["clock_format"] == "24h":
            time_format += "%H:%M"
        else:
            time_format += "%I:%M"
            
        if self.settings["show_seconds"]:
            time_format += ":%S"
            
        if self.settings["clock_format"] == "12h":
            time_format += " %p"

        time_str = datetime.now().strftime(time_format)
        
        if not self.standby_mode:
            if hasattr(self, 'clock_lbl'): self.clock_lbl.config(text=time_str)
        else:
            standby_fmt = "%H:%M:%S" if self.settings["show_seconds"] else "%H:%M"
            if hasattr(self, 'standby_clock'): self.standby_clock.config(text=datetime.now().strftime(standby_fmt))
            
        self.root.after(1000, self.update_clock)

    def process_network_queue(self):
        while not self.event_queue.empty():
            item = self.event_queue.get()
            evt_type = item[0]
            
            if evt_type == "LOG":
                self.add_log(item[1], item[2], item[3])
            elif evt_type == "PROXIMITY":
                if item[1] == "sleep" and not self.standby_mode:
                    self.trigger_standby()
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
        
        if self.view_mode == "details":
            self.update_display_values()

    def poll_network_loop(self):
        if NETWORK_AVAILABLE:
            self.sync_with_server_state(nc.get_state())
        self.root.after(UI_REFRESH_MS, self.poll_network_loop)

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