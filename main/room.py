import tkinter as tk
from tkinter import ttk
import math

class NexusLightOS:
    def __init__(self, root):
        self.root = root
        self.root.title("NEXUS LIGHT - Elite Smart Hospitality")
        
        try:
            self.root.attributes('-zoomed', True)
        except:
            self.root.state('zoomed')
            
        self.root.configure(bg="#f8fafc") 

        self.device_states = {}
        self.sidebar_widgets = {} 
        self.current_overlay = None
        
        self.rooms_data = [
            ("MASTER SUITE", "#eff6ff", "#2563eb"),   
            ("GUEST ROOM A", "#f0fdf4", "#16a34a"),  
            ("GUEST ROOM B", "#fffbeb", "#d97706"), 
            ("ROYAL LOUNGE", "#faf5ff", "#9333ea"),  
            ("DINING & KITCHEN", "#f1f5f9", "#475569"), 
        ]

        self.setup_styles()
        self.create_layout()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Nexus.Horizontal.TScale", 
                        background="#ffffff", 
                        troughcolor="#e2e8f0", 
                        sliderthickness=45, 
                        borderwidth=0)

    def create_layout(self):
        # Header
        self.top_bar = tk.Frame(self.root, bg="#ffffff", height=100)
        self.top_bar.pack(fill="x", side="top")
        self.top_bar.pack_propagate(False)
        tk.Label(self.top_bar, text="GRAND IMPERIAL SUITE", 
                 font=("DejaVu Sans", 32, "bold"), fg="#1e293b", bg="#ffffff").pack(side="left", padx=40)

        self.main_container = tk.Frame(self.root, bg="#f8fafc")
        self.main_container.pack(fill="both", expand=True)

        self.left_panel = tk.Frame(self.main_container, bg="#f8fafc")
        self.left_panel.place(relx=0, rely=0, relwidth=0.75, relheight=1)

        self.right_panel = tk.Frame(self.main_container, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1)
        self.right_panel.place(relx=0.75, rely=0, relwidth=0.25, relheight=1)

        self.setup_sidebar()
        
        self.canvas = tk.Canvas(self.left_panel, bg="#f8fafc", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=20, pady=20)
        self.canvas.bind("<Configure>", lambda e: self.draw_master_plan())

    def setup_sidebar(self):
        tk.Label(self.right_panel, text="QUICK CONTROLS", font=("DejaVu Sans", 22, "bold"), 
                 bg="#ffffff", fg="#0f172a", pady=30).pack()

        self.side_canvas = tk.Canvas(self.right_panel, bg="#ffffff", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.right_panel, orient="vertical", command=self.side_canvas.yview)
        self.scrollable_frame = tk.Frame(self.side_canvas, bg="#ffffff")

        # MODIFICA: La finestra interna ora si adatta alla larghezza del canvas per coprire tutto lo spazio
        self.side_canvas_window = self.side_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        def configure_scroll_region(e):
            self.side_canvas.configure(scrollregion=self.side_canvas.bbox("all"))
            # Forza la scrollable_frame a essere larga quanto il canvas
            self.side_canvas.itemconfig(self.side_canvas_window, width=e.width)

        self.side_canvas.bind("<Configure>", configure_scroll_region)
        self.side_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.side_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def draw_master_plan(self):
        self.canvas.delete("all")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w < 100: return 

        cols = 2
        rows = math.ceil(len(self.rooms_data) / cols) 
        gap = 20 
        
        card_w = (w - (gap * (cols + 1))) / cols
        card_h = (h - (gap * (rows + 1))) / rows

        for i, (name, color, accent) in enumerate(self.rooms_data):
            row, col = i // cols, i % cols
            x1, y1 = col * (card_w + gap) + gap, row * (card_h + gap) + gap
            x2, y2 = x1 + card_w, y1 + card_h
            
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="#cbd5e1", width=3, fill=color)
            self.canvas.create_text(x1 + (card_w/2), y1 + (card_h * 0.15), text=name, fill=accent, 
                                     font=("DejaVu Sans", 24, "bold"), 
                                     width=card_w-40, justify="center")
            
            devices = [("💡", "Lights"), ("🌡️", "Climate"), ("🎵", "Audio")]
            spacing = card_w / 4
            mid_y = y1 + (card_h * 0.6) 
            
            for j, (icon, dev_label) in enumerate(devices):
                ix = x1 + (spacing * (j + 1))
                full_name = f"{name} {dev_label}"
                
                if full_name not in self.device_states:
                    self.device_states[full_name] = tk.IntVar(value=50)

                node_size = min(card_h * 0.15, 50) 
                node = self.canvas.create_oval(ix-node_size, mid_y-node_size, ix+node_size, mid_y+node_size, 
                                               fill="white", outline="#e2e8f0", width=2)
                self.canvas.create_text(ix, mid_y, text=icon, font=("Noto Color Emoji", int(node_size * 0.8)))
                
                def open_pop(e, n=full_name, x=ix, y=mid_y): self.show_device_overlay(x, y, n)
                self.canvas.tag_bind(node, "<Button-1>", open_pop)
                
                self.add_sidebar_card(full_name, icon, accent)

    def add_sidebar_card(self, name, icon, accent):
        if name in self.sidebar_widgets: return 

        # MODIFICA: padx ridotto per permettere alle card di estendersi fino ai bordi laterali
        card = tk.Frame(self.scrollable_frame, bg="white", highlightbackground="#f1f5f9", highlightthickness=2, padx=10, pady=25)
        card.pack(fill="x", padx=5, pady=10)

        head = tk.Frame(card, bg="white")
        head.pack(fill="x")
        
        tk.Label(head, text=icon, font=("Noto Color Emoji", 32), bg="white").pack(side="left")
        tk.Label(head, text=name, font=("DejaVu Sans", 14, "bold"), bg="white", fg="#1e293b", 
                 wraplength=350, justify="left").pack(side="left", padx=15)

        s = ttk.Scale(card, from_=0, to=100, orient="horizontal", 
                      variable=self.device_states[name], style="Nexus.Horizontal.TScale")
        s.pack(fill="x", pady=(20, 0))
        self.sidebar_widgets[name] = card

    def show_device_overlay(self, x, y, dev_name):
        if self.current_overlay: self.current_overlay.destroy()
        overlay = tk.Frame(self.canvas, bg="white", highlightbackground="#2563eb", highlightthickness=3)
        self.current_overlay = overlay
        
        tk.Label(overlay, text=dev_name.upper(), font=("DejaVu Sans", 12, "bold"), 
                 bg="#2563eb", fg="white", pady=12).pack(fill="x")
        
        content = tk.Frame(overlay, bg="white", padx=30, pady=25)
        content.pack(fill="both")

        ttk.Scale(content, from_=0, to=100, variable=self.device_states[dev_name], 
                  style="Nexus.Horizontal.TScale").pack(fill="x", pady=20)

        tk.Button(content, text="SAVE CHANGES", command=overlay.destroy, bg="#1e293b", 
                  fg="white", font=("DejaVu Sans", 11, "bold"), bd=0, pady=12).pack(fill="x")
        
        overlay.place(x=x-150, y=y+60, width=300)

if __name__ == "__main__":
    root = tk.Tk()
    app = NexusLightOS(root)
    root.mainloop()