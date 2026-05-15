import tkinter as tk
from tkinter import ttk
from datetime import datetime


class NexusReceptionMonitor:

    def __init__(self, root):

        self.root = root
        self.root.title("TELKONET OMNIROOM - LUXURY CONTROL")
        self.root.geometry("1550x920")
        self.root.configure(bg="#F5F7FB")

        # ================= LUXURY COLORS =================
        self.colors = {
            "bg": "#F5F7FB",
            "card": "#FFFFFF",
            "blue": "#0B3A6A",
            "blue_soft": "#E8F1FF",
            "accent": "#2F80ED",
            "text": "#111827",
            "soft": "#6B7280",
            "border": "#E5EAF2",
            "green": "#18A558"
        }

        # ================= FONTS (INCREASED SIZE) =================
        self.font_h1 = ("Helvetica", 40, "bold")
        self.font_h2 = ("Helvetica", 26, "bold")
        self.font_h3 = ("Helvetica", 20, "bold")
        self.font_body = ("Helvetica", 16)
        self.font_small = ("Helvetica", 13)

        # ================= SUITES =================
        self.suites = ["SUITE 1", "SUITE 2", "SUITE 3", "SUITE 4", "SUITE 5"]

        self.rooms = ["ENTRY", "HALL", "BATH", "BEDROOM", "EN-SUITE", "KITCHENETTE", "LIVING"]

        # ================= DATA =================
        self.rooms_data = {}
        for suite in self.suites:
            for room in self.rooms:
                key = f"{suite} - {room}"
                self.rooms_data[key] = {
                    "lights": {"Ceiling": 25, "Floor lamp": 10, "Accent": 10, "Reading": 0},
                    "climate": 20,
                    "audio": 75,
                    "blinds": 0,
                    "active_scene": "Cinema"
                }

        self.selected_suite = tk.StringVar(value="SUITE 1")
        self.current_room = "ENTRY"

        self._style_ttk()
        self.create_widgets()
        self.update_clock()

    # ================= COMBOBOX STYLE =================
    def _style_ttk(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Luxury.TCombobox",
                        fieldbackground="#FFFFFF",
                        background="#FFFFFF",
                        foreground="#0B3A6A",
                        padding=14,
                        relief="flat",
                        font=("Helvetica", 18, "bold"))

        style.map("Luxury.TCombobox",
                  fieldbackground=[("readonly", "#FFFFFF")],
                  background=[("active", "#E8F1FF")])

    # ================= UI =================
    def create_widgets(self):

        header = tk.Frame(self.root, bg=self.colors["bg"])
        header.pack(fill="x", padx=30, pady=25)

        tk.Label(header,
                 text="TELKONET OMNIROOM",
                 font=self.font_h1,
                 bg=self.colors["bg"],
                 fg=self.colors["blue"]).pack(side="left")

        tk.Label(header,
                 text="Reception Control",
                 font=("Helvetica", 16),
                 bg=self.colors["bg"],
                 fg=self.colors["soft"]).pack(side="left", padx=20)

        self.clock_lbl = tk.Label(header,
                                  font=("Consolas", 24, "bold"),
                                  bg=self.colors["bg"],
                                  fg=self.colors["text"])
        self.clock_lbl.pack(side="right")

        main = tk.Frame(self.root, bg=self.colors["bg"])
        main.pack(fill="both", expand=True, padx=25)

        # LEFT
        left = tk.Frame(main, bg=self.colors["card"], width=320)
        left.pack(side="left", fill="y", padx=(0, 20))

        tk.Label(left,
                 text="SUITE SELECTION",
                 font=self.font_h3,
                 bg=self.colors["card"],
                 fg=self.colors["blue"]).pack(anchor="w", padx=18, pady=15)

        self.suite_menu = ttk.Combobox(left,
                                        textvariable=self.selected_suite,
                                        values=self.suites,
                                        state="readonly",
                                        style="Luxury.TCombobox")
        self.suite_menu.pack(fill="x", padx=18, pady=8)
        self.suite_menu.bind("<<ComboboxSelected>>", self.change_suite)

        tk.Label(left,
                 text="ROOMS",
                 font=self.font_small,
                 bg=self.colors["card"],
                 fg=self.colors["soft"]).pack(anchor="w", padx=18, pady=(25, 10))

        self.room_frame = tk.Frame(left, bg=self.colors["card"])
        self.room_frame.pack(fill="both", expand=True)

        self.create_room_buttons()

        # CENTER
        self.center = tk.Frame(main,
                               bg=self.colors["card"],
                               highlightbackground=self.colors["border"],
                               highlightthickness=1,
                               padx=40,
                               pady=35)
        self.center.pack(side="left", fill="both", expand=True)

        self.title_lbl = tk.Label(self.center,
                                  text="",
                                  font=self.font_h1,
                                  bg=self.colors["card"],
                                  fg=self.colors["blue"])
        self.title_lbl.pack(anchor="w")

        tk.Label(self.center,
                 text="SYSTEM ONLINE • ALL SERVICES ACTIVE",
                 font=self.font_small,
                 bg=self.colors["card"],
                 fg=self.colors["green"]).pack(anchor="w", pady=(5, 25))

        scene = tk.Frame(self.center, bg=self.colors["blue_soft"], padx=25, pady=18)
        scene.pack(fill="x", pady=(0, 25))

        tk.Label(scene,
                 text="ACTIVE SCENE",
                 font=self.font_small,
                 bg=self.colors["blue_soft"],
                 fg=self.colors["soft"]).pack(anchor="w")

        self.scene_lbl = tk.Label(scene,
                                  text="CINEMA",
                                  font=("Helvetica", 36, "bold"),
                                  bg=self.colors["blue_soft"],
                                  fg=self.colors["blue"])
        self.scene_lbl.pack(anchor="w")

        tk.Label(self.center,
                 text="ROOM DATA",
                 font=self.font_h3,
                 bg=self.colors["card"],
                 fg=self.colors["blue"]).pack(anchor="w", pady=15)

        self.labels = {}
        items = ["Ceiling Light", "Floor Lamp", "Accent Light",
                 "Reading Light", "Climate", "Audio", "Blinds"]

        for i in items:
            row = tk.Frame(self.center, bg=self.colors["card"])
            row.pack(fill="x", pady=10)

            tk.Label(row,
                     text=i,
                     font=self.font_body,
                     bg=self.colors["card"],
                     fg=self.colors["text"]).pack(side="left")

            val = tk.Label(row,
                           text="--",
                           font=("Helvetica", 18, "bold"),
                           bg=self.colors["card"],
                           fg=self.colors["accent"])
            val.pack(side="right")

            self.labels[i] = val

        log = tk.Frame(main, bg=self.colors["card"], width=300)
        log.pack(side="right", fill="y")

        tk.Label(log,
                 text="GUEST ACTIVITY LOG",
                 font=self.font_h3,
                 bg=self.colors["card"],
                 fg=self.colors["blue"]).pack(pady=15)

        self.log = tk.Text(log,
                           bg="#FFFFFF",
                           fg=self.colors["blue"],
                           font=("Consolas", 14),
                           state="disabled",
                           borderwidth=0)
        self.log.pack(fill="both", expand=True, padx=12, pady=10)

        self.select_room("ENTRY")

    # ================= ROOM BUTTONS =================
    def create_room_buttons(self):

        for w in self.room_frame.winfo_children():
            w.destroy()

        for room in self.rooms:

            btn = tk.Button(self.room_frame,
                            text=room,
                            font=("Helvetica", 15, "bold"),
                            bg="#FFFFFF",
                            fg=self.colors["blue"],
                            relief="flat",
                            bd=0,
                            padx=10,
                            pady=12,
                            activebackground=self.colors["blue"],
                            activeforeground="white",
                            command=lambda r=room: self.select_room(r))

            btn.pack(fill="x", padx=12, pady=7)

    # ================= LOGIC =================
    def change_suite(self, event=None):
        self.create_room_buttons()
        self.select_room("ENTRY")

    def select_room(self, room):

        suite = self.selected_suite.get()
        key = f"{suite} - {room}"
        self.current_room = key

        self.title_lbl.config(text=f"{suite} • {room}")

        data = self.rooms_data[key]

        self.labels["Ceiling Light"].config(text=f"{data['lights']['Ceiling']}%")
        self.labels["Floor Lamp"].config(text=f"{data['lights']['Floor lamp']}%")
        self.labels["Accent Light"].config(text=f"{data['lights']['Accent']}%")
        self.labels["Reading Light"].config(text=f"{data['lights']['Reading']}%")

        self.labels["Climate"].config(text=f"{data['climate']}°")
        self.labels["Audio"].config(text=f"{data['audio']}%")
        self.labels["Blinds"].config(text=f"{data['blinds']}%")

        self.scene_lbl.config(text=data["active_scene"].upper())
        self.add_log("SYSTEM", f"{suite} - {room}")

    def update_clock(self):
        self.clock_lbl.config(text=datetime.now().strftime("%d/%m/%Y  %H:%M:%S"))
        self.root.after(1000, self.update_clock)

    def add_log(self, src, msg):
        self.log.config(state="normal")
        self.log.insert("end",
                        f"[{datetime.now().strftime('%H:%M:%S')}] {src}: {msg}\n")
        self.log.see("end")
        self.log.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = NexusReceptionMonitor(root)
    root.mainloop()