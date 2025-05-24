import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as mpatches
import numpy as np
import psutil

class SystemMonitorUI:
    def __init__(self, root, backend):
        self.root = root
        self.backend = backend
        
        # Configure window
        self.root.title("System Resource Monitor")
        self.root.geometry("950x600")
        self.root.minsize(800, 550)
        
        # Set light theme colors
        self.bg_color = "#f5f5f5"
        self.fg_color = "#333333"
        self.cpu_color = "#0066cc"  # Blue
        self.memory_color = "#00cc66"  # Green
        self.disk_color = "#cc3300"  # Red
        
        # Apply theme
        self.apply_theme()
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.cpu_tab = ttk.Frame(self.notebook)
        self.memory_tab = ttk.Frame(self.notebook)
        self.disk_tab = ttk.Frame(self.notebook)
        self.network_tab = ttk.Frame(self.notebook)
        self.processes_tab = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.cpu_tab, text="CPU")
        self.notebook.add(self.memory_tab, text="Memory")
        self.notebook.add(self.disk_tab, text="Disk")
        self.notebook.add(self.network_tab, text="Network")
        self.notebook.add(self.processes_tab, text="Processes")
        
        # Setup tabs
        self.setup_cpu_tab()
        self.setup_memory_tab()
        self.setup_disk_tab()
        self.setup_network_tab()
        self.setup_processes_tab()
        
        # Create control frame
        self.control_frame = ttk.Frame(root)
        self.control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Refresh rate options
        ttk.Label(self.control_frame, text="Refresh Rate:").pack(side=tk.LEFT, padx=5)
        self.refresh_rate = tk.StringVar(value="1")
        refresh_combo = ttk.Combobox(self.control_frame, textvariable=self.refresh_rate, 
                                     values=["0.5", "1", "2", "5"], width=5)
        refresh_combo.pack(side=tk.LEFT, padx=5)
        ttk.Label(self.control_frame, text="seconds").pack(side=tk.LEFT)
        
        # Status bar
        self.status_bar = ttk.Label(root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind refresh rate change
        refresh_combo.bind("<<ComboboxSelected>>", self.update_refresh_rate)
        
        # Initialize processes list
        self.processes = []
        
        # Storage for disk UI elements
        self.disk_bars = []
        self.disk_labels = []
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def apply_theme(self):
        self.root.configure(bg=self.bg_color)
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors for various elements
        style.configure('TFrame', background=self.bg_color)
        style.configure('TLabel', background=self.bg_color, foreground=self.fg_color)
        style.configure('TButton', background=self.bg_color, foreground=self.fg_color)
        style.configure('TNotebook', background=self.bg_color)
        style.configure('TNotebook.Tab', background=self.bg_color, foreground=self.fg_color, padding=[10, 3])
        style.map('TNotebook.Tab', background=[('selected', '#ffffff')], 
                 foreground=[('selected', self.fg_color)])
        
        # Configure Progressbar styles
        style.configure("CPU.Horizontal.TProgressbar", 
                       troughcolor="#e0e0e0", 
                       background=self.cpu_color, 
                       borderwidth=0)
        
        style.configure("Memory.Horizontal.TProgressbar", 
                       troughcolor="#e0e0e0", 
                       background=self.memory_color, 
                       borderwidth=0)
        
        style.configure("Disk.Horizontal.TProgressbar", 
                       troughcolor="#e0e0e0", 
                       background=self.disk_color, 
                       borderwidth=0)
        
        # Configure Treeview
        style.configure("Treeview", 
                       background="#ffffff", 
                       foreground=self.fg_color, 
                       fieldbackground="#ffffff")
        style.map('Treeview', background=[('selected', '#e0e0e0')],
                 foreground=[('selected', self.fg_color)])
        
        # Configure Labelframe
        style.configure('TLabelframe', 
                       background=self.bg_color,
                       foreground=self.fg_color)
        style.configure('TLabelframe.Label', 
                       background=self.bg_color,
                       foreground=self.fg_color)
    
    def setup_cpu_tab(self):
        frame = ttk.Frame(self.cpu_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Get system info
        system_info = self.backend.get_system_info()
        
        # Top frame with info and pie chart
        top_frame = ttk.Frame(frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        # CPU info
        info_frame = ttk.LabelFrame(top_frame, text="CPU Information")
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        info_inner_frame = ttk.Frame(info_frame)
        info_inner_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(info_inner_frame, text=f"Logical CPUs:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        ttk.Label(info_inner_frame, text=f"{system_info['cpu_count']}", font=("Arial", 10, "bold")).grid(row=0, column=1, sticky=tk.W, padx=5, pady=3)
        
        ttk.Label(info_inner_frame, text=f"Physical Cores:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        ttk.Label(info_inner_frame, text=f"{system_info['physical_cores']}", font=("Arial", 10, "bold")).grid(row=1, column=1, sticky=tk.W, padx=5, pady=3)
        
        ttk.Label(info_inner_frame, text=f"Current Frequency:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=3)
        self.cpu_freq_label = ttk.Label(info_inner_frame, text="N/A", font=("Arial", 10, "bold"))
        self.cpu_freq_label.grid(row=2, column=1, sticky=tk.W, padx=5, pady=3)
        
        # CPU usage pie chart
        chart_frame = ttk.LabelFrame(top_frame, text="CPU Usage")
        chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        fig = Figure(figsize=(3, 3), dpi=100)
        self.cpu_pie_ax = fig.add_subplot(111)
        self.cpu_pie_ax.set_title("CPU Usage")
        
        # Initial empty pie chart
        self.cpu_pie = self.cpu_pie_ax.pie([0, 100], colors=[self.cpu_color, '#e0e0e0'], 
                                          startangle=90, shadow=False, 
                                          wedgeprops={'edgecolor': 'white', 'linewidth': 2})
        self.cpu_pie_ax.text(0, 0, "0%", ha='center', va='center', fontsize=20, fontweight='bold')
        
        self.cpu_pie_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        self.cpu_pie_canvas.draw()
        self.cpu_pie_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # CPU usage
        usage_frame = ttk.LabelFrame(frame, text="CPU Core Usage")
        usage_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Overall CPU usage
        ttk.Label(usage_frame, text="Overall CPU Usage:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.cpu_overall_bar = ttk.Progressbar(usage_frame, length=400, mode="determinate", style="CPU.Horizontal.TProgressbar")
        self.cpu_overall_bar.grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        self.cpu_overall_label = ttk.Label(usage_frame, text="0%", font=("Arial", 10, "bold"))
        self.cpu_overall_label.grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
        
        # Per-core usage
        self.cpu_bars = []
        self.cpu_labels = []
        
        cores_frame = ttk.Frame(usage_frame)
        cores_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W+tk.E, padx=10, pady=5)
        
        # Show cores in a grid layout to save space
        cores_per_row = 4
        for i in range(system_info['cpu_count']):
            row = (i // cores_per_row) + 1
            col = i % cores_per_row
            
            ttk.Label(cores_frame, text=f"Core {i}:").grid(row=row, column=col*3, sticky=tk.W, padx=5, pady=2)
            bar = ttk.Progressbar(cores_frame, length=100, mode="determinate", style="CPU.Horizontal.TProgressbar")
            bar.grid(row=row, column=col*3+1, sticky=tk.W, padx=5, pady=2)
            label = ttk.Label(cores_frame, text="0%")
            label.grid(row=row, column=col*3+2, sticky=tk.W, padx=5, pady=2)
            
            self.cpu_bars.append(bar)
            self.cpu_labels.append(label)
        
        # CPU history graph
        graph_frame = ttk.LabelFrame(frame, text="CPU History")
        graph_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        fig = Figure(figsize=(5, 2), dpi=100)
        
        self.cpu_ax = fig.add_subplot(111)
        self.cpu_ax.set_title("CPU Usage Over Time")
        self.cpu_ax.set_xlabel("Time (seconds)")
        self.cpu_ax.set_ylabel("Usage (%)")
        self.cpu_ax.set_ylim(0, 100)
        
        # Create empty line for CPU usage
        self.cpu_line, = self.cpu_ax.plot([], [], label="CPU", color=self.cpu_color, linewidth=2)
        
        self.cpu_ax.legend(loc="upper left")
        self.cpu_ax.grid(True, linestyle='--', alpha=0.7)
        
        # Create canvas
        self.cpu_canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        self.cpu_canvas.draw()
        self.cpu_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_memory_tab(self):
        frame = ttk.Frame(self.memory_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top frame with info and pie chart
        top_frame = ttk.Frame(frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        # Memory info
        info_frame = ttk.LabelFrame(top_frame, text="Memory Information")
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        mem = psutil.virtual_memory()
        total_gb = mem.total / (1024 ** 3)
        
        info_inner_frame = ttk.Frame(info_frame)
        info_inner_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(info_inner_frame, text=f"Total Memory:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        ttk.Label(info_inner_frame, text=f"{total_gb:.2f} GB", font=("Arial", 10, "bold")).grid(row=0, column=1, sticky=tk.W, padx=5, pady=3)
        
        ttk.Label(info_inner_frame, text="Available:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        self.memory_available = ttk.Label(info_inner_frame, text="0 GB", font=("Arial", 10, "bold"))
        self.memory_available.grid(row=1, column=1, sticky=tk.W, padx=5, pady=3)
        
        ttk.Label(info_inner_frame, text="Used:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=3)
        self.memory_used = ttk.Label(info_inner_frame, text="0 GB", font=("Arial", 10, "bold"))
        self.memory_used.grid(row=2, column=1, sticky=tk.W, padx=5, pady=3)
        
        # Memory pie chart
        chart_frame = ttk.LabelFrame(top_frame, text="Memory Usage")
        chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        fig = Figure(figsize=(3, 3), dpi=100)
        self.memory_pie_ax = fig.add_subplot(111)
        
        # Initial empty pie chart
        self.memory_pie = self.memory_pie_ax.pie([0, 0, 100], 
                                               colors=[self.memory_color, '#66ccff', '#e0e0e0'], 
                                               startangle=90, shadow=False,
                                               wedgeprops={'edgecolor': 'white', 'linewidth': 2})
        
        # Add legend
        self.memory_pie_ax.legend(['Used', 'Cached', 'Free'], loc="lower center", bbox_to_anchor=(0.5, -0.15), ncol=3)
        
        self.memory_pie_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        self.memory_pie_canvas.draw()
        self.memory_pie_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Memory usage
        usage_frame = ttk.LabelFrame(frame, text="Memory Usage")
        usage_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # RAM usage
        ttk.Label(usage_frame, text="RAM Usage:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.memory_bar = ttk.Progressbar(usage_frame, length=400, mode="determinate", style="Memory.Horizontal.TProgressbar")
        self.memory_bar.grid(row=0, column=1, sticky=tk.W+tk.E, padx=10, pady=5)
        self.memory_label = ttk.Label(usage_frame, text="0 / 0 GB (0%)", font=("Arial", 10, "bold"))
        self.memory_label.grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
        
        # Memory history graph
        graph_frame = ttk.LabelFrame(frame, text="Memory History")
        graph_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        fig = Figure(figsize=(5, 2), dpi=100)
        
        self.memory_ax = fig.add_subplot(111)
        self.memory_ax.set_title("Memory Usage Over Time")
        self.memory_ax.set_xlabel("Time (seconds)")
        self.memory_ax.set_ylabel("Usage (%)")
        self.memory_ax.set_ylim(0, 100)
        
        # Create empty line for memory usage
        self.memory_line, = self.memory_ax.plot([], [], label="Memory", color=self.memory_color, linewidth=2)
        
        self.memory_ax.legend(loc="upper left")
        self.memory_ax.grid(True, linestyle='--', alpha=0.7)
        
        # Create canvas
        self.memory_canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        self.memory_canvas.draw()
        self.memory_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_disk_tab(self):
        frame = ttk.Frame(self.disk_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top frame with I/O info and pie chart
        top_frame = ttk.Frame(frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        # Disk I/O
        io_frame = ttk.LabelFrame(top_frame, text="Disk I/O")
        io_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        io_inner_frame = ttk.Frame(io_frame)
        io_inner_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(io_inner_frame, text="Read:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        self.disk_read_label = ttk.Label(io_inner_frame, text="0 MB/s", font=("Arial", 10, "bold"))
        self.disk_read_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=3)
        
        ttk.Label(io_inner_frame, text="Write:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        self.disk_write_label = ttk.Label(io_inner_frame, text="0 MB/s", font=("Arial", 10, "bold"))
        self.disk_write_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=3)
        
        # Disk usage pie chart (will be updated with first partition)
        chart_frame = ttk.LabelFrame(top_frame, text="Disk Usage")
        chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        fig = Figure(figsize=(3, 3), dpi=100)
        self.disk_pie_ax = fig.add_subplot(111)
        
        # Initial empty pie chart
        self.disk_pie = self.disk_pie_ax.pie([0, 100], colors=[self.disk_color, '#e0e0e0'], 
                                           startangle=90, shadow=False,
                                           wedgeprops={'edgecolor': 'white', 'linewidth': 2})
        self.disk_pie_ax.text(0, 0, "0%", ha='center', va='center', fontsize=20, fontweight='bold')
        
        self.disk_pie_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        self.disk_pie_canvas.draw()
        self.disk_pie_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Disk partitions
        partitions_frame = ttk.LabelFrame(frame, text="Disk Partitions")
        partitions_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create scrollable frame for partitions
        canvas = tk.Canvas(partitions_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(partitions_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
        
        # Get disk partitions
        partitions = self.backend.get_disk_partitions()
        
        # Disk partitions
        self.disk_bars = []
        self.disk_labels = []
        
        for i, partition in enumerate(partitions):
            ttk.Label(scrollable_frame, text=f"{partition['device']} ({partition['mountpoint']})", font=("Arial", 10, "bold")).grid(row=i*2, column=0, columnspan=3, sticky=tk.W, padx=5, pady=3)
            
            ttk.Label(scrollable_frame, text=f"Type: {partition['fstype']} | Total: {partition['total'] / (1024**3):.2f} GB").grid(row=i*2+1, column=0, sticky=tk.W, padx=5, pady=2)
            
            bar = ttk.Progressbar(scrollable_frame, length=300, mode="determinate", style="Disk.Horizontal.TProgressbar")
            bar.grid(row=i*2+1, column=1, sticky=tk.W+tk.E, padx=5, pady=2)
            label = ttk.Label(scrollable_frame, text=f"{partition['used'] / (1024**3):.2f} / {partition['total'] / (1024**3):.2f} GB ({partition['percent']:.1f}%)")
            label.grid(row=i*2+1, column=2, sticky=tk.W, padx=5, pady=2)
            
            bar['value'] = partition['percent']
            
            self.disk_bars.append((partition['mountpoint'], bar))
            self.disk_labels.append((partition['mountpoint'], label))
            
            # Use first partition for pie chart
            if i == 0:
                self.update_disk_pie(partition['percent'])
        
        # Disk history graph
        graph_frame = ttk.LabelFrame(frame, text="Disk I/O History")
        graph_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        fig = Figure(figsize=(5, 2), dpi=100)
        
        self.disk_ax = fig.add_subplot(111)
        self.disk_ax.set_title("Disk I/O Over Time")
        self.disk_ax.set_xlabel("Time (seconds)")
        self.disk_ax.set_ylabel("MB/s")
        
        # Create empty line for disk I/O
        self.disk_line, = self.disk_ax.plot([], [], label="Disk I/O", color=self.disk_color, linewidth=2)
        
        self.disk_ax.legend(loc="upper left")
        self.disk_ax.grid(True, linestyle='--', alpha=0.7)
        
        # Create canvas
        self.disk_canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        self.disk_canvas.draw()
        self.disk_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_network_tab(self):
        frame = ttk.Frame(self.network_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Network usage
        usage_frame = ttk.LabelFrame(frame, text="Network Usage")
        usage_frame.pack(fill=tk.X, pady=5)
        
        usage_inner_frame = ttk.Frame(usage_frame)
        usage_inner_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(usage_inner_frame, text="Sent:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        self.net_sent_label = ttk.Label(usage_inner_frame, text="0 KB/s", font=("Arial", 10, "bold"))
        self.net_sent_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=3)
        
        ttk.Label(usage_inner_frame, text="Received:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        self.net_recv_label = ttk.Label(usage_inner_frame, text="0 KB/s", font=("Arial", 10, "bold"))
        self.net_recv_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=3)
        
        # Network interfaces
        interfaces_frame = ttk.LabelFrame(frame, text="Network Interfaces")
        interfaces_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create scrollable frame for interfaces
        canvas = tk.Canvas(interfaces_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(interfaces_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
        
        # Get network interfaces
        interfaces = self.backend.get_network_interfaces()
        
        # Network interfaces
        row = 0
        for interface in interfaces:
            ttk.Label(scrollable_frame, text=f"Interface: {interface['name']}", font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, sticky=tk.W, padx=5, pady=3)
            row += 1
            
            for addr in interface['addresses']:
                ttk.Label(scrollable_frame, text=f"{addr['type']} Address:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
                ttk.Label(scrollable_frame, text=f"{addr['address']}").grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
                row += 1
            
            ttk.Separator(scrollable_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=5)
            row += 1
        
        # Network history graph
        graph_frame = ttk.LabelFrame(frame, text="Network Traffic History")
        graph_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        fig = Figure(figsize=(5, 2), dpi=100)
        
        self.network_ax = fig.add_subplot(111)
        self.network_ax.set_title("Network Traffic Over Time")
        self.network_ax.set_xlabel("Time (seconds)")
        self.network_ax.set_ylabel("KB/s")
        
        # Create empty line for network traffic
        self.network_line, = self.network_ax.plot([], [], label="Network I/O", color="#9933cc", linewidth=2)
        
        self.network_ax.legend(loc="upper left")
        self.network_ax.grid(True, linestyle='--', alpha=0.7)
        
        # Create canvas
        self.network_canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        self.network_canvas.draw()
        self.network_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_processes_tab(self):
        frame = ttk.Frame(self.processes_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Controls
        controls_frame = ttk.Frame(frame)
        controls_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(controls_frame, text="Sort by:").pack(side=tk.LEFT, padx=5)
        self.sort_var = tk.StringVar(value="CPU")
        sort_combo = ttk.Combobox(controls_frame, textvariable=self.sort_var, 
                                 values=["CPU", "Memory", "Name", "PID"], width=10)
        sort_combo.pack(side=tk.LEFT, padx=5)
        sort_combo.bind("<<ComboboxSelected>>", self.sort_processes)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_processes)
        ttk.Label(controls_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        search_entry = ttk.Entry(controls_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = ttk.Button(controls_frame, text="Refresh", command=self.refresh_processes)
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        # Process list
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create treeview with scrollbar
        columns = ("pid", "name", "cpu", "memory", "status")
        self.process_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Define headings
        self.process_tree.heading("pid", text="PID")
        self.process_tree.heading("name", text="Name")
        self.process_tree.heading("cpu", text="CPU %")
        self.process_tree.heading("memory", text="Memory")
        self.process_tree.heading("status", text="Status")
        
        # Define columns
        self.process_tree.column("pid", width=70)
        self.process_tree.column("name", width=250)
        self.process_tree.column("cpu", width=70)
        self.process_tree.column("memory", width=100)
        self.process_tree.column("status", width=100)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.process_tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient="horizontal", command=self.process_tree.xview)
        self.process_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.process_tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')
        
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        # Process details
        details_frame = ttk.LabelFrame(frame, text="Process Details")
        details_frame.pack(fill=tk.X, pady=5)
        
        self.process_details = ttk.Label(details_frame, text="Select a process to view details")
        self.process_details.pack(fill=tk.X, padx=10, pady=10)
        
        # Bind select event
        self.process_tree.bind("<<TreeviewSelect>>", self.show_process_details)
    
    def update_refresh_rate(self, event=None):
        """Update the refresh rate in the backend"""
        try:
            rate = float(self.refresh_rate.get())
            self.backend.set_update_interval(rate)
        except ValueError:
            pass
    
    def update_cpu_pie(self, percent):
        """Update the CPU pie chart"""
        self.cpu_pie_ax.clear()
        self.cpu_pie = self.cpu_pie_ax.pie([percent, 100-percent], 
                                          colors=[self.cpu_color, '#e0e0e0'], 
                                          startangle=90, shadow=False,
                                          wedgeprops={'edgecolor': 'white', 'linewidth': 2})
        self.cpu_pie_ax.text(0, 0, f"{percent:.1f}%", ha='center', va='center', fontsize=20, fontweight='bold')
        self.cpu_pie_canvas.draw_idle()
    
    def update_memory_pie(self, memory_breakdown):
        """Update the memory pie chart"""
        total = sum(memory_breakdown.values())
        if total == 0:
            return
            
        used_percent = memory_breakdown['used'] / total * 100
        cached_percent = memory_breakdown['cached'] / total * 100
        free_percent = memory_breakdown['free'] / total * 100
        
        self.memory_pie_ax.clear()
        self.memory_pie = self.memory_pie_ax.pie([used_percent, cached_percent, free_percent], 
                                               colors=[self.memory_color, '#66ccff', '#e0e0e0'], 
                                               startangle=90, shadow=False,
                                               wedgeprops={'edgecolor': 'white', 'linewidth': 2})
        
        # Add legend
        self.memory_pie_ax.legend(['Used', 'Cached', 'Free'], loc="lower center", bbox_to_anchor=(0.5, -0.15), ncol=3)
        self.memory_pie_canvas.draw_idle()
    
    def update_disk_pie(self, percent):
        """Update the disk pie chart"""
        self.disk_pie_ax.clear()
        self.disk_pie = self.disk_pie_ax.pie([percent, 100-percent], 
                                           colors=[self.disk_color, '#e0e0e0'], 
                                           startangle=90, shadow=False,
                                           wedgeprops={'edgecolor': 'white', 'linewidth': 2})
        self.disk_pie_ax.text(0, 0, f"{percent:.1f}%", ha='center', va='center', fontsize=20, fontweight='bold')
        self.disk_pie_canvas.draw_idle()
    
    def update_ui(self):
        """Update the UI with the latest data from the backend"""
        data = self.backend.get_update()
        if not data:
            return
        
        # Update CPU tab
        self.cpu_overall_bar['value'] = data['cpu_percent']
        self.cpu_overall_label.config(text=f"{data['cpu_percent']:.1f}%")
        self.cpu_freq_label.config(text=data['cpu_freq'])
        
        # Update CPU pie chart
        self.update_cpu_pie(data['cpu_percent'])
        
        for i, percent in enumerate(data['cpu_percents']):
            if i < len(self.cpu_bars):
                self.cpu_bars[i]['value'] = percent
                self.cpu_labels[i].config(text=f"{percent:.1f}%")
        
        # Update memory tab
        self.memory_bar['value'] = data['memory_percent']
        self.memory_label.config(text=f"{data['memory_used_gb']:.2f} / {data['memory_total_gb']:.2f} GB ({data['memory_percent']:.1f}%)")
        self.memory_available.config(text=f"{data['memory_available_gb']:.2f} GB")
        self.memory_used.config(text=f"{data['memory_used_gb']:.2f} GB")
        
        # Update memory pie chart
        self.update_memory_pie(data['memory_breakdown'])
        
        # Update disk tab
        for (mountpoint, bar), (disk_mountpoint, usage) in zip(self.disk_bars, data['disk_partitions']):
            if mountpoint == disk_mountpoint:
                bar['value'] = usage.percent
                
                for mountpoint_label, label in self.disk_labels:
                    if mountpoint_label == disk_mountpoint:
                        used_gb = usage.used / (1024 ** 3)
                        total_gb = usage.total / (1024 ** 3)
                        label.config(text=f"{used_gb:.2f} / {total_gb:.2f} GB ({usage.percent:.1f}%)")
                        break
        
        self.disk_read_label.config(text=f"{data['disk_read_rate']:.2f} MB/s")
        self.disk_write_label.config(text=f"{data['disk_write_rate']:.2f} MB/s")
        
        # Update network tab
        self.net_sent_label.config(text=f"{data['net_sent_rate']:.2f} KB/s")
        self.net_recv_label.config(text=f"{data['net_recv_rate']:.2f} KB/s")
        
        # Update graphs
        self.update_graphs(data)
    
    def update_graphs(self, data):
        """Update all graphs with new data"""
        try:
            # Time axis (60 seconds)
            time_axis = list(range(-59, 1))
            
            # CPU graph
            self.cpu_line.set_data(time_axis, data['cpu_history'])
            self.cpu_ax.relim()
            self.cpu_ax.autoscale_view()
            self.cpu_canvas.draw_idle()
            
            # Memory graph
            self.memory_line.set_data(time_axis, data['memory_history'])
            self.memory_ax.relim()
            self.memory_ax.autoscale_view()
            self.memory_canvas.draw_idle()
            
            # Disk graph
            self.disk_line.set_data(time_axis, data['disk_io_history'])
            self.disk_ax.relim()
            self.disk_ax.autoscale_view()
            self.disk_canvas.draw_idle()
            
            # Network graph
            self.network_line.set_data(time_axis, data['net_io_history'])
            self.network_ax.relim()
            self.network_ax.autoscale_view()
            self.network_canvas.draw_idle()
            
        except Exception as e:
            print(f"Error updating graphs: {str(e)}")
    
    def refresh_processes(self):
        """Refresh the process list"""
        try:
            # Get process list from backend
            self.processes = self.backend.get_processes()
            
            # Sort processes
            self.sort_processes()
            
            # Update status
            self.status_bar.config(text=f"Processes: {len(self.processes)}")
        except Exception as e:
            print(f"Error refreshing processes: {str(e)}")
    
    def sort_processes(self, event=None):
        """Sort processes based on selected criteria"""
        sort_by = self.sort_var.get()
        
        if sort_by == "CPU":
            self.processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        elif sort_by == "Memory":
            self.processes.sort(key=lambda x: x['memory_mb'], reverse=True)
        elif sort_by == "Name":
            self.processes.sort(key=lambda x: x['name'].lower())
        elif sort_by == "PID":
            self.processes.sort(key=lambda x: x['pid'])
        
        # Apply filter and update display
        self.filter_processes()
    
    def filter_processes(self, *args):
        """Filter processes based on search text"""
        search_text = self.search_var.get().lower()
        
        # Clear existing items
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        
        # Add filtered processes (limit to top 100 for performance)
        count = 0
        for proc in self.processes:
            if count >= 100:
                break
                
            if search_text in str(proc['pid']).lower() or search_text in proc['name'].lower():
                self.process_tree.insert('', 'end', values=(
                    proc['pid'],
                    proc['name'],
                    f"{proc['cpu_percent']:.1f}",
                    f"{proc['memory_mb']:.1f} MB",
                    proc['status']
                ))
                count += 1
    
    def show_process_details(self, event):
        """Show details for selected process"""
        selected_item = self.process_tree.selection()
        if not selected_item:
            return
        
        pid = int(self.process_tree.item(selected_item[0], 'values')[0])
        
        # Get process details from backend
        details = self.backend.get_process_details(pid)
        
        if 'error' in details:
            self.process_details.config(text=details['error'])
            return
        
        # Format details
        details_text = f"Process: {details['name']} (PID: {pid})\n"
        details_text += f"Executable: {details['exe']}\n"
        details_text += f"Command Line: {details['cmdline']}\n"
        details_text += f"User: {details['username']}"
        
        self.process_details.config(text=details_text)
    
    def start_ui_update(self):
        """Start the UI update loop"""
        self.update_ui()
        self.root.after(100, self.start_ui_update)
    
    def on_close(self):
        """Handle window close event"""
        self.backend.stop()
        self.root.destroy()