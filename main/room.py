import tkinter as tk
from tkinter import ttk

class NexusLightOS:
    def __init__(self, root):
        self.root = root
        self.root.title("NEXUS LIGHT OS - High Visibility Mode")
        self.dark_mode = False
        
        try:
            self.root.attributes('-zoomed', True)
        except:
            self.root.state('zoomed')
            
        self.bg_main = "#f1f5f9"
        self.bg_sidebar = "#ffffff"
        self.fg_text = "#1e293b"
        self.root.configure(bg=self.bg_main) 

        self.device_states = {}
        self.sidebar_widgets = {} 
        
        self.blueprint_data = {
            "BEDROOM 1": {"rect": (0.05, 0.05, 0.30, 0.35), "color": "#eff6ff", "dark_color": "#1e293b"},
            "BEDROOM 2": {"rect": (0.35, 0.05, 0.25, 0.35), "color": "#eff6ff", "dark_color": "#1e293b"},
            "BATH 1":    {"rect": (0.05, 0.40, 0.15, 0.20), "color": "#f0f9ff", "dark_color": "#0f172a"},
            "UTILITY":   {"rect": (0.05, 0.60, 0.20, 0.30), "color": "#f8fafc", "dark_color": "#334155"},
            "HALL":      {"rect": (0.20, 0.40, 0.30, 0.20), "color": "#ffffff", "dark_color": "#1e293b"},
            "BATH 2":    {"rect": (0.25, 0.60, 0.25, 0.30), "color": "#f0f9ff", "dark_color": "#0f172a"},
            "LIVING":    {"rect": (0.60, 0.05, 0.35, 0.45), "color": "#faf5ff", "dark_color": "#1e1b4b"},
            "KITCHEN":   {"rect": (0.60, 0.50, 0.35, 0.40), "color": "#fff7ed", "dark_color": "#431407"},
            "ENTRY":     {"rect": (0.50, 0.40, 0.10, 0.30), "color": "#f1f5f9", "dark_color": "#334155"},
        }

        self.setup_styles()
        self.create_layout()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Nexus.Horizontal.TScale", background="#ffffff", troughcolor="#e2e8f0", sliderthickness=25)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        # Definisci i colori base
        self.bg_main = "#0f172a" if self.dark_mode else "#f1f5f9"
        self.bg_sidebar = "#1e293b" if self.dark_mode else "#ffffff"
        self.fg_text = "#f8fafc" if self.dark_mode else "#1e293b"
        
        # Applica ai container
        self.root.configure(bg=self.bg_main)
        self.main_container.configure(bg=self.bg_main)
        self.left_panel.configure(bg=self.bg_main)
        self.canvas.configure(bg=self.bg_main)
        self.right_panel.configure(bg=self.bg_sidebar, highlightbackground="#334155" if self.dark_mode else "#cbd5e1")
        self.side_canvas.configure(bg=self.bg_sidebar)
        self.scrollable_frame.configure(bg=self.bg_sidebar)
        self.sidebar_title.configure(bg=self.bg_sidebar, fg=self.fg_text)
        
        # Aggiorna widget sidebar
        for dev_id, card in self.sidebar_widgets.items():
            card.configure(bg=self.bg_sidebar, highlightbackground="#334155" if self.dark_mode else "#e2e8f0")
            for child in card.winfo_children():
                if isinstance(child, tk.Label):
                    child.configure(bg=self.bg_sidebar, fg=self.fg_text)
        
        self.draw_blueprint()

    def create_layout(self):
        self.top_bar = tk.Frame(self.root, bg="#1e293b", height=70)
        self.top_bar.pack(fill="x", side="top")
        
        tk.Label(self.top_bar, text="NEXUS LIGHT | DASHBOARD", font=("Helvetica", 22, "bold"), fg="#f8fafc", bg="#1e293b").pack(side="left", padx=30)
        
        # Bottone Toggle Theme
        tk.Button(self.top_bar, text="🌓 TOGGLE MODE", font=("Helvetica", 10, "bold"), 
                  command=self.toggle_theme, bg="#334155", fg="white", bd=0, padx=20, pady=5, cursor="hand2").pack(side="right", padx=30)

        self.main_container = tk.Frame(self.root, bg=self.bg_main)
        self.main_container.pack(fill="both", expand=True)

        self.left_panel = tk.Frame(self.main_container, bg=self.bg_main)
        self.left_panel.place(relx=0, rely=0, relwidth=0.68, relheight=1)

        self.right_panel = tk.Frame(self.main_container, bg=self.bg_sidebar, highlightthickness=1, highlightbackground="#cbd5e1")
        self.right_panel.place(relx=0.68, rely=0, relwidth=0.32, relheight=1)

        self.sidebar_title = tk.Label(self.right_panel, text="PARAMETERS", font=("Helvetica", 16, "bold"), bg=self.bg_sidebar, fg=self.fg_text, pady=25)
        self.sidebar_title.pack(fill="x")
        
        self.side_canvas = tk.Canvas(self.right_panel, bg=self.bg_sidebar, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.right_panel, orient="vertical", command=self.side_canvas.yview)
        self.scrollable_frame = tk.Frame(self.side_canvas, bg=self.bg_sidebar)
        
        self.side_canvas_frame = self.side_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.side_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.side_canvas.bind("<Configure>", lambda e: self.side_canvas.itemconfig(self.side_canvas_frame, width=e.width))
        
        self.side_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas = tk.Canvas(self.left_panel, bg=self.bg_main, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=20, pady=20)
        self.canvas.bind("<Configure>", lambda e: self.draw_blueprint())

    def draw_door(self, x, y, size=40, type="H", flip=False):
        color = "#94a3b8" if self.dark_mode else "#475569"
        bg_color = self.bg_main 
        
        if type == "H":
            self.canvas.create_line(x, y, x + size, y, fill=bg_color, width=5)
            if not flip:
                self.canvas.create_line(x, y, x, y - size, fill=color, width=2)
                self.canvas.create_arc(x - size, y - size, x + size, y + size, start=90, extent=-90, style="arc", outline=color)
            else:
                self.canvas.create_line(x, y, x, y + size, fill=color, width=2)
                self.canvas.create_arc(x - size, y - size, x + size, y + size, start=270, extent=90, style="arc", outline=color)
        else:
            self.canvas.create_line(x, y, x, y + size, fill=bg_color, width=5)
            if not flip:
                self.canvas.create_line(x, y, x + size, y, fill=color, width=2)
                self.canvas.create_arc(x - size, y - size, x + size, y + size, start=0, extent=-90, style="arc", outline=color)
            else:
                self.canvas.create_line(x, y, x - size, y, fill=color, width=2)
                self.canvas.create_arc(x - size, y - size, x + size, y + size, start=180, extent=90, style="arc", outline=color)

    def add_to_sidebar(self, room_name, dev_id, icon):
        if dev_id in self.sidebar_widgets: return
        card = tk.Frame(self.scrollable_frame, bg=self.bg_sidebar, highlightthickness=1, highlightbackground="#e2e8f0", pady=15)
        card.pack(fill="x", padx=20, pady=8)
        lbl_top = tk.Label(card, text=f"{icon} {room_name}", font=("Helvetica", 12, "bold"), bg=self.bg_sidebar, fg=self.fg_text, anchor="w")
        lbl_top.pack(fill="x", padx=15)
        scale = ttk.Scale(card, from_=0, to=100, variable=self.device_states[dev_id], style="Nexus.Horizontal.TScale")
        scale.pack(fill="x", padx=15, pady=10)
        self.sidebar_widgets[dev_id] = card

    def draw_blueprint(self):
        self.canvas.delete("all")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w < 100: return 

        device_types = [("💡", 0.2), ("🌡️", 0.4), ("🎵", 0.6), ("🪟", 0.8)]

        for name, data in self.blueprint_data.items():
            rx, ry, rw, rh = data["rect"]
            x1, y1, x2, y2 = rx*w, ry*h, (rx+rw)*w, (ry+rh)*h
            room_color = data["dark_color"] if self.dark_mode else data["color"]
            outline_color = "#f8fafc" if self.dark_mode else "#1e293b"
            
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=room_color, outline=outline_color, width=3)
            self.canvas.create_text(x1+15, y1+20, text=name, anchor="nw", font=("Helvetica", 11, "bold"), fill=outline_color)

            for sym, offset_x in device_types:
                ix, iy = x1 + (rw*w*offset_x), y1 + (rh*h*0.6)
                dev_id = f"{name}_{sym}"
                if dev_id not in self.device_states:
                    self.device_states[dev_id] = tk.IntVar(value=50)
                r = 22
                self.canvas.create_oval(ix-r, iy-r, ix+r, iy+r, fill="#1e293b" if self.dark_mode else "white", outline="#334155" if self.dark_mode else "#cbd5e1", width=2)
                self.canvas.create_text(ix, iy, text=sym, font=("Arial", 16), fill="white" if self.dark_mode else "black")
                self.add_to_sidebar(name, dev_id, sym)

        # --- PORTE ---
        self.draw_door(0.20 * w, 0.40 * h, type="H", flip=True) 
        self.draw_door(0.35 * w, 0.40 * h, type="H", flip=True)
        self.draw_door(0.20 * w, 0.45 * h, type="V", flip=False)
        self.draw_door(0.20 * w, 0.65 * h, type="V", flip=False)
        self.draw_door(0.50 * w, 0.65 * h, type="V", flip=True)
        self.draw_door(0.60 * w, 0.25 * h, type="V", flip=True)
        self.draw_door(0.75 * w, 0.50 * h, type="H", flip=False)
        self.draw_door(0.50 * w, 0.55 * h, type="V", flip=False)

        self.scrollable_frame.update_idletasks()
        self.side_canvas.config(scrollregion=self.side_canvas.bbox("all"))

if __name__ == "__main__":
    root = tk.Tk()
    app = NexusLightOS(root)
    root.mainloop()