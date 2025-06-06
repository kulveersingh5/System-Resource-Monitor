# System-Resource-Monitor
The Resource Allocation Tracker presented in the code is a comprehensive System Resource Monitoring Tool developed using Python. It provides a graphical user interface (GUI) to track and visualize real-time system metrics, including:
1. CPU usage (overall and per-core)
2. Memory utilization
3. Disk activity and usage
4. Network traffic
5. Running processes and their resource consumption
The application offers interactive components like pie charts, line graphs, and progress bars, with data refreshed at customizable intervals. It’s ideal for monitoring system health and diagnosing performance bottlenecks in real time.

## 🛠️ Technologies Used
1. Python
Core programming language

2. Tkinter
GUI framework for rendering windows, tabs, and controls

3. Matplotlib
For plotting dynamic pie charts and line graphs

4. Psutil
For gathering system performance data (CPU, memory, disk, network, processes)

5. Threading
To handle background data collection without freezing the UI

6. ttk (Themed Tkinter Widgets)
For a modernized, styled user interface

7. Platform, Socket, Queue
For retrieving system-level details and managing thread-safe data flow