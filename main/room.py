import tkinter as tk
from tkinter import ttk

class NexusLightOS:
    def __init__(self, root):
        self.root = root
        self.root.title("NEXUS LIGHT - Elite Smart Hospitality")
        
        # Geometria ottimizzata per schermi laptop e desktop
        self.root.geometry("1300x850")
        self.root.configure(bg="#0f172a") 

        self.device_states = {}
        self.current_overlay = None
        
        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Nexus.Horizontal.TScale", 
                        background="#ffffff", 
                        troughcolor="#f1f5f9", 
                        sliderthickness=25, 
                        borderwidth=0)
        style.map("Nexus.Horizontal.TScale",
                  background=[('pressed', '#6366f1'), ('active', '#818cf8')])

    def create_widgets(self):
        self.main_content = tk.Frame(self.root, bg="#f8fafc")
        self.main_content.pack(fill="both", expand=True)

        # TOP BAR
        top_bar = tk.Frame(self.main_content, bg="#ffffff", pady=25, padx=50)
        top_bar.pack(fill="x")
        
        title_frame = tk.Frame(top_bar, bg="#ffffff")
        title_frame.pack(side="left")
        
        tk.Label(title_frame, text="GRAND IMPERIAL SUITE", 
                 font=("Helvetica", 32, "bold"), fg="#1e293b", bg="#ffffff").pack(anchor="w")
        
        tk.Label(title_frame, text="● SYSTEM ONLINE  |  ELITE ACCESS CONTROL", 
                 font=("Helvetica", 10, "bold"), fg="#10b981", bg="#ffffff").pack(anchor="w")

        # CANVAS AREA
        self.canvas_container = tk.Frame(self.main_content, bg="#f8fafc")
        self.canvas_container.pack(fill="both", expand=True, padx=40, pady=20)

        self.canvas = tk.Canvas(self.canvas_container, bg="#f8fafc", highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Aspettiamo che la finestra sia pronta per calcolare le posizioni
        self.root.after(100, self.draw_master_plan)

    def draw_master_plan(self):
        self.canvas.delete("all")
        
        # Coordinate proporzionali per evitare che escano dallo schermo
        # (x1, y1, x2, y2, Nome, Colore Sfondo, Colore Testo)
        rooms = [
            (20, 20, 400, 320, "MASTER SUITE", "#eff6ff", "#2563eb"),   
            (420, 20, 750, 320, "GUEST ROOM A", "#f0fdf4", "#16a34a"),  
            (770, 20, 1100, 320, "GUEST ROOM B", "#fffbeb", "#d97706"), 
            (20, 350, 500, 680, "ROYAL LOUNGE", "#faf5ff", "#9333ea"),  
            (520, 350, 1100, 680, "DINING & KITCHEN", "#f8fafc", "#475569"), 
        ]

        for x1, y1, x2, y2, name, color, accent in rooms:
            # Rettangolo Stanza
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="#cbd5e1", width=2, fill=color, tags="room")
            
            # Label Stanza
            self.canvas.create_text(x1+25, y1+35, text=name, anchor="w", 
                                     fill=accent, font=("Helvetica", 18, "bold"))
            
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            
            # Nodi di controllo (Icone grandi)
            self.add_smart_node(mid_x - 100, mid_y, "💡", f"Lights - {name}", "DIMMER", y2)
            self.add_smart_node(mid_x, mid_y, "🌡️", f"Climate - {name}", "TEMP", y2)
            self.add_smart_node(mid_x + 100, mid_y, "🎵", f"Audio - {name}", "VOL", y2)

    def add_smart_node(self, x, y, icon, name, type_key, room_bottom):
        radius = 40
        node = self.canvas.create_oval(x-radius, y-radius, x+radius, y+radius, 
                                       fill="white", outline="#e2e8f0", width=2)
        
        txt = self.canvas.create_text(x, y, text=icon, fill="#1e293b", font=("Segoe UI Emoji", 24))
        
        # Passiamo anche la coordinata 'room_bottom' per decidere dove aprire l'overlay
        def on_click(e): self.show_pro_overlay(x, y, name, type_key, room_bottom)
        
        for item in [node, txt]:
            self.canvas.tag_bind(item, "<Button-1>", on_click)
            self.canvas.tag_bind(item, "<Enter>", lambda e: self.canvas.itemconfig(node, outline="#6366f1", width=4))
            self.canvas.tag_bind(item, "<Leave>", lambda e: self.canvas.itemconfig(node, outline="#e2e8f0", width=2))

    def show_pro_overlay(self, x, y, dev_name, dev_type, room_bottom):
        if self.current_overlay: self.current_overlay.destroy()

        overlay = tk.Frame(self.canvas, bg="white", highlightbackground="#6366f1", highlightthickness=2)
        self.current_overlay = overlay
        
        # LOGICA ANTI-BORDO: Se il bottone è troppo in basso, apri l'overlay SOPRA il bottone
        overlay_height = 300
        if y + overlay_height > 750: # Controllo se esce dal basso
            pos_y = y - overlay_height - 10
        else:
            pos_y = y + 50

        overlay.place(x=x-150, y=pos_y, width=300)

        # Header
        header = tk.Frame(overlay, bg="#6366f1", padx=15, pady=12)
        header.pack(fill="x")
        tk.Label(header, text=dev_name.upper(), font=("Helvetica", 9, "bold"), 
                 fg="white", bg="#6366f1").pack(anchor="w")

        # Body
        body = tk.Frame(overlay, bg="white", padx=25, pady=20)
        body.pack(fill="both")

        controls = {"DIMMER": ("Intensity", "Brightness"), "VOL": ("Volume", "Audio level"), "TEMP": ("Climate", "Temperature")}
        label, sub = controls.get(dev_type, ("Control", "Adjust"))
        
        tk.Label(body, text=label, fg="#1e293b", bg="white", font=("Helvetica", 16, "bold")).pack(anchor="w")
        tk.Label(body, text=sub, fg="#94a3b8", bg="white", font=("Helvetica", 10)).pack(anchor="w")
        
        val_slider = ttk.Scale(body, from_=0, to=100, orient="horizontal", style="Nexus.Horizontal.TScale")
        val_slider.set(self.device_states.get(dev_name, 50))
        val_slider.pack(fill="x", pady=20)

        save_btn = tk.Button(body, text="CONFIRM", 
                             command=lambda: self.save_state(dev_name, val_slider, save_btn, overlay), 
                             bg="#1e293b", fg="white", font=("Helvetica", 12, "bold"), 
                             bd=0, pady=12, cursor="hand2")
        save_btn.pack(fill="x")
        
        tk.Button(body, text="Close", command=overlay.destroy, bg="white", 
                  fg="#94a3b8", font=("Helvetica", 10), bd=0, cursor="hand2").pack(fill="x", pady=5)

    def save_state(self, dev_name, slider, btn, overlay):
        self.device_states[dev_name] = int(slider.get())
        btn.config(text="SAVED ✓", bg="#10b981")
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