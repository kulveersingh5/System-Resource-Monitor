import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class SystemMonitorUI:
    def __init__(self, root, backend):
        self.root = root
        self.backend = backend
        
        # Color scheme: white, red, blue, green
        self.colors = {
            'white': '#ffffff',
            'red': '#dc3545',
            'blue': '#007bff', 
            'green': '#28a745',
            'light_gray': '#f8f9fa',
            'dark_gray': '#6c757d'
        }
        
        # Configure window
        self.root.title("System Resource Monitor")
        self.root.geometry("1000x700")
        self.root.configure(bg=self.colors['white'])
        
        # Apply theme
        self.setup_theme()
        
        # Create interface
        self.create_interface()
        
        # Initialize data
        self.processes = []
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def setup_theme(self):
        """Setup theme"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('TNotebook', background=self.colors['white'])
        style.configure('TNotebook.Tab', padding=[12, 8])
        style.map('TNotebook.Tab', 
                 background=[('selected', self.colors['blue'])],
                 foreground=[('selected', self.colors['white'])])
        
        style.configure('TFrame', background=self.colors['white'])
        style.configure('TLabel', background=self.colors['white'])
        style.configure('TButton', padding=[8, 4])
        
        # Progress bars
        style.configure("Red.Horizontal.TProgressbar", 
                       background=self.colors['red'], troughcolor=self.colors['light_gray'])
        style.configure("Blue.Horizontal.TProgressbar", 
                       background=self.colors['blue'], troughcolor=self.colors['light_gray'])
        style.configure("Green.Horizontal.TProgressbar", 
                       background=self.colors['green'], troughcolor=self.colors['light_gray'])
    
    def create_interface(self):
        """Create main interface"""
        # Header
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(header, text="System Resource Monitor", 
                 font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        
        # Refresh rate
        ttk.Label(header, text="Refresh:").pack(side=tk.RIGHT, padx=(0, 5))
        self.refresh_var = tk.StringVar(value="1")
        refresh_combo = ttk.Combobox(header, textvariable=self.refresh_var, 
                                    values=["1", "2", "5"], width=5, state="readonly")
        refresh_combo.pack(side=tk.RIGHT)
        
        # Notebook with 6 tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create tabs
        self.cpu_tab = ttk.Frame(self.notebook)
        self.memory_tab = ttk.Frame(self.notebook)
        self.disk_tab = ttk.Frame(self.notebook)
        self.network_tab = ttk.Frame(self.notebook)
        self.processes_tab = ttk.Frame(self.notebook)
        self.commands_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.cpu_tab, text="CPU")
        self.notebook.add(self.memory_tab, text="Memory")
        self.notebook.add(self.disk_tab, text="Disk")
        self.notebook.add(self.network_tab, text="Network")
        self.notebook.add(self.processes_tab, text="Processes")
        self.notebook.add(self.commands_tab, text="Commands")
        
        # Setup all tabs
        self.setup_cpu_tab()
        self.setup_memory_tab()
        self.setup_disk_tab()
        self.setup_network_tab()
        self.setup_processes_tab()
        self.setup_commands_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
    
    def setup_cpu_tab(self):
        """Setup CPU tab"""
        # CPU Info
        info_frame = ttk.LabelFrame(self.cpu_tab, text="CPU Information", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.cpu_info_label = ttk.Label(info_frame, text="Loading CPU info...")
        self.cpu_info_label.pack(anchor=tk.W)
        
        # CPU Usage
        usage_frame = ttk.LabelFrame(self.cpu_tab, text="CPU Usage", padding=10)
        usage_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Overall usage
        overall_frame = ttk.Frame(usage_frame)
        overall_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(overall_frame, text="Overall CPU:").pack(side=tk.LEFT)
        self.cpu_bar = ttk.Progressbar(overall_frame, length=300, mode="determinate", 
                                      style="Red.Horizontal.TProgressbar")
        self.cpu_bar.pack(side=tk.LEFT, padx=(10, 10))
        self.cpu_label = ttk.Label(overall_frame, text="0%", font=('Arial', 12, 'bold'))
        self.cpu_label.pack(side=tk.LEFT)
        
        # Per-core usage
        self.cores_frame = ttk.Frame(usage_frame)
        self.cores_frame.pack(fill=tk.X, pady=5)
        self.cpu_core_bars = []
        self.cpu_core_labels = []
        
        # CPU Chart
        chart_frame = ttk.LabelFrame(self.cpu_tab, text="CPU Usage History", padding=10)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        fig = Figure(figsize=(8, 3), dpi=80, facecolor='white')
        self.cpu_ax = fig.add_subplot(111)
        self.cpu_ax.set_title("CPU Usage Over Time")
        self.cpu_ax.set_ylabel("Usage (%)")
        self.cpu_ax.set_ylim(0, 100)
        self.cpu_ax.grid(True, alpha=0.3)
        
        self.cpu_line, = self.cpu_ax.plot([], [], color=self.colors['red'], linewidth=2)
        
        self.cpu_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        self.cpu_canvas.draw()
        self.cpu_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def setup_memory_tab(self):
        """Setup Memory tab"""
        # Memory Info
        info_frame = ttk.LabelFrame(self.memory_tab, text="Memory Information", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.memory_info_label = ttk.Label(info_frame, text="Loading memory info...")
        self.memory_info_label.pack(anchor=tk.W)
        
        # Memory Usage
        usage_frame = ttk.LabelFrame(self.memory_tab, text="Memory Usage", padding=10)
        usage_frame.pack(fill=tk.X, padx=10, pady=5)
        
        usage_bar_frame = ttk.Frame(usage_frame)
        usage_bar_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(usage_bar_frame, text="Memory:").pack(side=tk.LEFT)
        self.memory_bar = ttk.Progressbar(usage_bar_frame, length=300, mode="determinate", 
                                         style="Blue.Horizontal.TProgressbar")
        self.memory_bar.pack(side=tk.LEFT, padx=(10, 10))
        self.memory_label = ttk.Label(usage_bar_frame, text="0%", font=('Arial', 12, 'bold'))
        self.memory_label.pack(side=tk.LEFT)
        
        # Memory Chart
        chart_frame = ttk.LabelFrame(self.memory_tab, text="Memory Usage History", padding=10)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        fig = Figure(figsize=(8, 3), dpi=80, facecolor='white')
        self.memory_ax = fig.add_subplot(111)
        self.memory_ax.set_title("Memory Usage Over Time")
        self.memory_ax.set_ylabel("Usage (%)")
        self.memory_ax.set_ylim(0, 100)
        self.memory_ax.grid(True, alpha=0.3)
        
        self.memory_line, = self.memory_ax.plot([], [], color=self.colors['blue'], linewidth=2)
        
        self.memory_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        self.memory_canvas.draw()
        self.memory_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def setup_disk_tab(self):
        """Setup Disk tab"""
        # Disk Usage
        usage_frame = ttk.LabelFrame(self.disk_tab, text="Disk Usage", padding=10)
        usage_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create scrollable frame for disks
        canvas = tk.Canvas(usage_frame, bg=self.colors['white'])
        scrollbar = ttk.Scrollbar(usage_frame, orient="vertical", command=canvas.yview)
        self.disk_scrollable_frame = ttk.Frame(canvas)
        
        self.disk_scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.disk_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.disk_bars = []
        self.disk_labels = []
        
        # Disk I/O
        io_frame = ttk.LabelFrame(self.disk_tab, text="Disk I/O", padding=10)
        io_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.disk_io_label = ttk.Label(io_frame, text="Read: 0 MB/s | Write: 0 MB/s")
        self.disk_io_label.pack()
    
    def setup_network_tab(self):
        """Setup Network tab"""
        # Network I/O
        io_frame = ttk.LabelFrame(self.network_tab, text="Network I/O", padding=10)
        io_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.network_io_label = ttk.Label(io_frame, text="Sent: 0 KB/s | Received: 0 KB/s")
        self.network_io_label.pack()
        
        # Network Interfaces
        interfaces_frame = ttk.LabelFrame(self.network_tab, text="Network Interfaces", padding=10)
        interfaces_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create scrollable frame for interfaces
        canvas = tk.Canvas(interfaces_frame, bg=self.colors['white'])
        scrollbar = ttk.Scrollbar(interfaces_frame, orient="vertical", command=canvas.yview)
        self.network_scrollable_frame = ttk.Frame(canvas)
        
        self.network_scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.network_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Network Chart
        chart_frame = ttk.LabelFrame(self.network_tab, text="Network Activity History", padding=10)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        fig = Figure(figsize=(8, 2), dpi=80, facecolor='white')
        self.network_ax = fig.add_subplot(111)
        self.network_ax.set_title("Network Activity Over Time")
        self.network_ax.set_ylabel("KB/s")
        self.network_ax.grid(True, alpha=0.3)
        
        self.network_line, = self.network_ax.plot([], [], color=self.colors['green'], linewidth=2)
        
        self.network_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        self.network_canvas.draw()
        self.network_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def setup_processes_tab(self):
        """Setup Processes tab"""
        # Controls
        controls = ttk.Frame(self.processes_tab)
        controls.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(controls, text="Refresh", command=self.refresh_processes).pack(side=tk.LEFT)
        ttk.Button(controls, text="Kill Process", command=self.kill_process).pack(side=tk.LEFT, padx=(10, 0))
        
        # Process list
        list_frame = ttk.Frame(self.processes_tab)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("pid", "name", "cpu", "memory", "status")
        self.process_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        self.process_tree.heading("pid", text="PID")
        self.process_tree.heading("name", text="Process Name")
        self.process_tree.heading("cpu", text="CPU %")
        self.process_tree.heading("memory", text="Memory %")
        self.process_tree.heading("status", text="Status")
        
        self.process_tree.column("pid", width=80)
        self.process_tree.column("name", width=250)
        self.process_tree.column("cpu", width=80)
        self.process_tree.column("memory", width=80)
        self.process_tree.column("status", width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=scrollbar.set)
        
        self.process_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_commands_tab(self):
        """Setup Commands tab with updated 6 commands"""
        # Command buttons
        buttons_frame = ttk.LabelFrame(self.commands_tab, text="System Commands", padding=10)
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Updated commands: removed diskpart and chkdsk, added systeminfo and hostname
        commands = ['Ping', 'IP Config', 'Task List', 'System Info', 'Hostname', 'Echo Hello']
        
        # Create 2 rows of 3 buttons each
        for i, cmd in enumerate(commands):
            row = i // 3
            col = i % 3
            
            btn = ttk.Button(buttons_frame, text=cmd, 
                           command=lambda c=cmd: self.execute_command(c))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        # Configure grid weights
        for i in range(3):
            buttons_frame.grid_columnconfigure(i, weight=1)
        
        # Output
        output_frame = ttk.LabelFrame(self.commands_tab, text="Command Output", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Output controls
        output_controls = ttk.Frame(output_frame)
        output_controls.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(output_controls, text="Clear", command=self.clear_output).pack(side=tk.RIGHT)
        
        # Output text
        self.output_text = tk.Text(output_frame, height=15, font=('Consolas', 9),
                                  bg=self.colors['light_gray'])
        output_scroll = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=output_scroll.set)
        
        self.output_text.pack(side="left", fill="both", expand=True)
        output_scroll.pack(side="right", fill="y")
    
    def execute_command(self, command):
        """Execute a command"""
        self.output_text.insert(tk.END, f"\n> {command}\n")
        self.output_text.insert(tk.END, "-" * 40 + "\n")
        self.output_text.see(tk.END)
        self.root.update()
        
        # Send to backend
        self.backend.command_queue.put(('execute', command))
    
    def clear_output(self):
        """Clear command output"""
        self.output_text.delete(1.0, tk.END)
    
    def refresh_processes(self):
        """Refresh process list"""
        self.processes = self.backend.get_processes()
        
        # Clear tree
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        
        # Add processes
        for proc in self.processes:
            self.process_tree.insert('', 'end', values=(
                proc['pid'],
                proc['name'],
                f"{proc['cpu_percent']:.1f}",
                f"{proc['memory_percent']:.1f}",
                proc['status']
            ))
        
        self.status_var.set(f"Processes: {len(self.processes)}")
    
    def kill_process(self):
        """Kill selected process"""
        selection = self.process_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a process")
            return
        
        item = selection[0]
        values = self.process_tree.item(item, 'values')
        pid = int(values[0])
        name = values[1]
        
        if messagebox.askyesno("Confirm", f"Kill process {name} (PID: {pid})?"):
            self.backend.command_queue.put(('kill_process', pid))
    
    def update_ui(self):
        """Update UI with latest data"""
        # Get data update
        data = self.backend.get_update()
        if data:
            self.update_cpu_tab(data['cpu'], data['cpu_history'])
            self.update_memory_tab(data['memory'], data['memory_history'])
            self.update_disk_tab(data['disk'], data['disk_history'], data['disk_rate'])
            self.update_network_tab(data['network'], data['network_history'], data['network_rate'])
        
        # Get command results
        result = self.backend.get_command_result()
        if result:
            result_type, data = result
            
            if result_type == 'command_result':
                if data['success']:
                    self.output_text.insert(tk.END, data['output'] + "\n\n")
                else:
                    self.output_text.insert(tk.END, f"Error: {data['output']}\n\n")
                self.output_text.see(tk.END)
            
            elif result_type == 'kill_result':
                if data['success']:
                    messagebox.showinfo("Success", data['message'])
                    self.refresh_processes()
                else:
                    messagebox.showerror("Error", data['message'])
    
    def update_cpu_tab(self, cpu_data, cpu_history):
        """Update CPU tab"""
        # Update info
        info_text = f"CPU Cores: {cpu_data['cpu_count']} | Physical: {cpu_data['physical_cores']} | Frequency: {cpu_data['current_freq']:.0f} MHz"
        self.cpu_info_label.config(text=info_text)
        
        # Update overall usage
        self.cpu_bar['value'] = cpu_data['cpu_percent']
        self.cpu_label.config(text=f"{cpu_data['cpu_percent']:.1f}%")
        
        # Update per-core usage
        per_cpu = cpu_data['per_cpu']
        
        # Create core bars if not exist
        if len(self.cpu_core_bars) != len(per_cpu):
            # Clear existing
            for widget in self.cores_frame.winfo_children():
                widget.destroy()
            self.cpu_core_bars = []
            self.cpu_core_labels = []
            
            # Create new
            for i, percent in enumerate(per_cpu):
                core_frame = ttk.Frame(self.cores_frame)
                core_frame.pack(fill=tk.X, pady=1)
                
                ttk.Label(core_frame, text=f"Core {i}:", width=8).pack(side=tk.LEFT)
                bar = ttk.Progressbar(core_frame, length=150, mode="determinate", 
                                     style="Red.Horizontal.TProgressbar")
                bar.pack(side=tk.LEFT, padx=(5, 10))
                label = ttk.Label(core_frame, text=f"{percent:.1f}%", width=6)
                label.pack(side=tk.LEFT)
                
                self.cpu_core_bars.append(bar)
                self.cpu_core_labels.append(label)
        
        # Update core bars
        for i, (bar, label, percent) in enumerate(zip(self.cpu_core_bars, self.cpu_core_labels, per_cpu)):
            bar['value'] = percent
            label.config(text=f"{percent:.1f}%")
        
        # Update chart
        time_axis = list(range(len(cpu_history)))
        self.cpu_line.set_data(time_axis, cpu_history)
        self.cpu_ax.relim()
        self.cpu_ax.autoscale_view()
        self.cpu_canvas.draw_idle()
    
    def update_memory_tab(self, memory_data, memory_history):
        """Update Memory tab"""
        # Update info
        info_text = f"Total: {memory_data['total_gb']:.1f} GB | Used: {memory_data['used_gb']:.1f} GB | Available: {memory_data['available_gb']:.1f} GB"
        self.memory_info_label.config(text=info_text)
        
        # Update usage bar
        self.memory_bar['value'] = memory_data['percent']
        self.memory_label.config(text=f"{memory_data['percent']:.1f}%")
        
        # Update chart
        time_axis = list(range(len(memory_history)))
        self.memory_line.set_data(time_axis, memory_history)
        self.memory_ax.relim()
        self.memory_ax.autoscale_view()
        self.memory_canvas.draw_idle()
    
    def update_disk_tab(self, disk_data, disk_history, disk_rate):
        """Update Disk tab"""
        # Update I/O
        self.disk_io_label.config(text=f"Disk I/O Rate: {disk_rate:.2f} MB/s")
        
        # Update disk usage
        partitions = disk_data['partitions']
        
        # Create disk bars if not exist or count changed
        if len(self.disk_bars) != len(partitions):
            # Clear existing
            for widget in self.disk_scrollable_frame.winfo_children():
                widget.destroy()
            self.disk_bars = []
            self.disk_labels = []
            
            # Create new
            for i, partition in enumerate(partitions):
                disk_frame = ttk.Frame(self.disk_scrollable_frame)
                disk_frame.pack(fill=tk.X, pady=5)
                
                ttk.Label(disk_frame, text=f"{partition['device']}", 
                         font=('Arial', 10, 'bold')).pack(anchor=tk.W)
                
                usage_frame = ttk.Frame(disk_frame)
                usage_frame.pack(fill=tk.X, pady=2)
                
                bar = ttk.Progressbar(usage_frame, length=300, mode="determinate", 
                                     style="Green.Horizontal.TProgressbar")
                bar.pack(side=tk.LEFT, padx=(0, 10))
                
                label = ttk.Label(usage_frame, text="")
                label.pack(side=tk.LEFT)
                
                self.disk_bars.append(bar)
                self.disk_labels.append(label)
        
        # Update disk bars
        for i, (bar, label, partition) in enumerate(zip(self.disk_bars, self.disk_labels, partitions)):
            bar['value'] = partition['percent']
            label.config(text=f"{partition['used_gb']:.1f} / {partition['total_gb']:.1f} GB ({partition['percent']:.1f}%)")
    
    def update_network_tab(self, network_data, network_history, network_rate):
        """Update Network tab"""
        # Update I/O
        self.network_io_label.config(text=f"Network Rate: {network_rate:.1f} KB/s")
        
        # Update interfaces (only once)
        if not hasattr(self, 'network_interfaces_created'):
            interfaces = network_data['interfaces']
            
            for i, interface in enumerate(interfaces):
                interface_frame = ttk.Frame(self.network_scrollable_frame)
                interface_frame.pack(fill=tk.X, pady=5)
                
                status = "UP" if interface['is_up'] else "DOWN"
                ttk.Label(interface_frame, text=f"{interface['name']} ({status})", 
                         font=('Arial', 10, 'bold')).pack(anchor=tk.W)
                
                for addr in interface['addresses']:
                    addr_frame = ttk.Frame(interface_frame)
                    addr_frame.pack(fill=tk.X, padx=20)
                    
                    ttk.Label(addr_frame, text=f"{addr['type']}: {addr['address']}").pack(anchor=tk.W)
            
            self.network_interfaces_created = True
        
        # Update chart
        time_axis = list(range(len(network_history)))
        self.network_line.set_data(time_axis, network_history)
        self.network_ax.relim()
        self.network_ax.autoscale_view()
        self.network_canvas.draw_idle()
    
    def start_update_loop(self):
        """Start UI update loop"""
        self.update_ui()
        self.root.after(100, self.start_update_loop)
    
    def on_close(self):
        """Handle window close"""
        self.backend.stop()
        self.root.destroy()

if __name__ == "__main__":
    print("System Monitor UI - Ready")