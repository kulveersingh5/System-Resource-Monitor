import tkinter as tk
from backend import SystemMonitor
from frontend import SystemMonitorUI

def main():
    """System Monitor Application with Separate Tabs"""
    print("Starting System Monitor with Separate Tabs...")
    
    # Create root window
    root = tk.Tk()
    
    # Create backend
    backend = SystemMonitor(update_interval=1.0)
    
    # Create frontend
    frontend = SystemMonitorUI(root, backend)
    
    # Start backend
    backend.start()
    
    # Start UI updates
    frontend.start_update_loop()
    
    # Initial process refresh
    root.after(2000, frontend.refresh_processes)
    
    print("System Monitor Started!")
    print("\nAvailable Tabs:")
    print("1. CPU - CPU usage, cores, frequency")
    print("2. Memory - RAM usage and history")
    print("3. Disk - Disk usage and I/O")
    print("4. Network - Network interfaces and activity")
    print("5. Processes - Running processes management")
    print("6. Commands - System commands execution")
    
    print("\nAvailable Commands:")
    for i, cmd in enumerate(backend.get_commands(), 1):
        print(f"  {i}. {cmd}")
    
    try:
        # Run application
        root.mainloop()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        backend.stop()
    
    print("System Monitor Closed")

if __name__ == "__main__":
    main()