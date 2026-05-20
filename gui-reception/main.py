import tkinter as tk
import logging

from network_client import start

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

def main():
    start()
    root=tk.Tk()
    root.title("Reception GUI")
    root.geometry("1550x920")
    root.configure(bg="#F5F7FB")
    root.resizable(True, True)
    
    app=tk.Frame()
    app.pack(fill="both", expand=True)
    root.mainloop()
    
if __name__=="__main__":
    main()