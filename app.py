import tkinter as tk
from backend import SystemMonitorBackend
from frontend import SystemMonitorUI

def main():
    # Create the root window
    root = tk.Tk()
    
    # Create the backend
    backend = SystemMonitorBackend(update_interval=1.0)
    
    # Create the frontend
    frontend = SystemMonitorUI(root, backend)
    
    # Start the backend data collection
    backend.start()
    
    # Start the UI update loop
    frontend.start_ui_update()
    
    # Refresh processes initially
    root.after(1000, frontend.refresh_processes)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main()