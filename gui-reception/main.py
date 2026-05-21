import sys
import os
import logging
import tkinter as tk

# Calculate paths relative to this file's position
current_dir = os.path.dirname(os.path.abspath(__file__))
views_dir = os.path.join(current_dir, "views")
sys.path.append(views_dir)

# Import network and the newly renamed view module
from network_client import start
from gui_reception import NexusReceptionMonitor

# Configurazione del log
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

def main():
    start()
    root = tk.Tk()
    app = NexusReceptionMonitor(root)
    root.mainloop()
    
if __name__ == "__main__":
    main()