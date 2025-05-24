import psutil
import platform
import threading
import time
import socket
from datetime import datetime
import queue

class SystemMonitorBackend:
    def __init__(self, update_interval=1.0):
        # Create data structures for historical data
        self.cpu_history = [0] * 60
        self.memory_history = [0] * 60
        self.disk_io_history = [0] * 60
        self.net_io_history = [0] * 60
        
        # Previous values for rate calculations
        self.prev_disk_read = 0
        self.prev_disk_write = 0
        self.prev_net_sent = 0
        self.prev_net_recv = 0
        self.prev_time = time.time()
        
        # Create a queue for thread-safe updates
        self.update_queue = queue.Queue()
        
        # Set update interval
        self.update_interval = update_interval
        
        # Thread control
        self.running = True
        self.update_thread = None
    
    def start(self):
        """Start the data collection thread"""
        self.running = True
        self.update_thread = threading.Thread(target=self.update_data)
        self.update_thread.daemon = True
        self.update_thread.start()
    
    def stop(self):
        """Stop the data collection thread"""
        self.running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1.0)
    
    def get_system_info(self):
        """Get basic system information"""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'processor': platform.processor(),
            'cpu_count': psutil.cpu_count(logical=True),
            'physical_cores': psutil.cpu_count(logical=False)
        }
    
    def get_disk_partitions(self):
        """Get disk partition information"""
        partitions = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                })
            except PermissionError:
                pass
        return partitions
    
    def get_network_interfaces(self):
        """Get network interface information"""
        interfaces = []
        for interface, addrs in psutil.net_if_addrs().items():
            addresses = []
            for addr in addrs:
                addr_type = None
                if addr.family == socket.AF_INET:
                    addr_type = 'IPv4'
                elif addr.family == socket.AF_INET6:
                    addr_type = 'IPv6'
                elif hasattr(socket, 'AF_PACKET') and addr.family == socket.AF_PACKET:
                    addr_type = 'MAC'
                
                if addr_type:
                    addresses.append({
                        'type': addr_type,
                        'address': addr.address
                    })
            
            interfaces.append({
                'name': interface,
                'addresses': addresses
            })
        return interfaces
    
    def get_processes(self):
        """Get process information"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                pinfo = proc.info
                # Calculate memory in MB
                memory_mb = pinfo['memory_percent'] * psutil.virtual_memory().total / (1024 ** 2) / 100
                
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'cpu_percent': pinfo['cpu_percent'],
                    'memory_mb': memory_mb,
                    'status': pinfo['status']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return processes
    
    def get_process_details(self, pid):
        """Get detailed information about a specific process"""
        try:
            proc = psutil.Process(pid)
            return {
                'name': proc.name(),
                'exe': proc.exe() if hasattr(proc, 'exe') else "N/A",
                'cmdline': ' '.join(proc.cmdline()) if hasattr(proc, 'cmdline') else "N/A",
                'username': proc.username() if hasattr(proc, 'username') else "N/A",
                'status': proc.status() if hasattr(proc, 'status') else "N/A",
                'cpu_percent': proc.cpu_percent() if hasattr(proc, 'cpu_percent') else "N/A",
                'memory_percent': proc.memory_percent() if hasattr(proc, 'memory_percent') else "N/A"
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return {'error': 'Process information not available'}
    
    def update_data(self):
        """Background thread to update system data"""
        while self.running:
            try:
                # Get current time
                current_time = time.time()
                time_diff = current_time - self.prev_time
                
                # CPU data
                cpu_percent = psutil.cpu_percent()
                cpu_percents = psutil.cpu_percent(percpu=True)
                
                try:
                    cpu_freq = psutil.cpu_freq()
                    if cpu_freq:
                        cpu_freq_text = f"{cpu_freq.current:.2f} MHz"
                    else:
                        cpu_freq_text = "N/A"
                except:
                    cpu_freq_text = "N/A"
                
                # Memory data
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                memory_used_gb = memory.used / (1024 ** 3)
                memory_total_gb = memory.total / (1024 ** 3)
                memory_available_gb = memory.available / (1024 ** 3)
                memory_cached_gb = getattr(memory, 'cached', 0) / (1024 ** 3)
                
                # Memory breakdown for pie chart
                memory_breakdown = {
                    'used': memory.used - getattr(memory, 'cached', 0),
                    'cached': getattr(memory, 'cached', 0),
                    'free': memory.available
                }
                
                # Disk I/O
                disk_io = psutil.disk_io_counters()
                if disk_io:
                    disk_read = disk_io.read_bytes
                    disk_write = disk_io.write_bytes
                    
                    # Calculate rates
                    disk_read_rate = (disk_read - self.prev_disk_read) / time_diff / (1024 ** 2)  # MB/s
                    disk_write_rate = (disk_write - self.prev_disk_write) / time_diff / (1024 ** 2)  # MB/s
                    
                    self.prev_disk_read = disk_read
                    self.prev_disk_write = disk_write
                    
                    # Combined disk I/O for history
                    disk_io_rate = disk_read_rate + disk_write_rate
                else:
                    disk_read_rate = 0
                    disk_write_rate = 0
                    disk_io_rate = 0
                
                # Network data
                net_io = psutil.net_io_counters()
                if net_io:
                    net_sent = net_io.bytes_sent
                    net_recv = net_io.bytes_recv
                    
                    # Calculate rates
                    net_sent_rate = (net_sent - self.prev_net_sent) / time_diff / 1024  # KB/s
                    net_recv_rate = (net_recv - self.prev_net_recv) / time_diff / 1024  # KB/s
                    
                    self.prev_net_sent = net_sent
                    self.prev_net_recv = net_recv
                    
                    # Combined network I/O for history
                    net_io_rate = net_sent_rate + net_recv_rate
                else:
                    net_sent_rate = 0
                    net_recv_rate = 0
                    net_io_rate = 0
                
                # Update history
                self.cpu_history.append(cpu_percent)
                self.cpu_history.pop(0)
                
                self.memory_history.append(memory_percent)
                self.memory_history.pop(0)
                
                self.disk_io_history.append(disk_io_rate)
                self.disk_io_history.pop(0)
                
                self.net_io_history.append(net_io_rate)
                self.net_io_history.pop(0)
                
                # Update previous time
                self.prev_time = current_time
                
                # Get disk partitions usage
                disk_partitions = []
                for partition in psutil.disk_partitions():
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        disk_partitions.append((partition.mountpoint, usage))
                    except:
                        pass
                
                # Put data in queue for UI thread
                self.update_queue.put({
                    'cpu_percent': cpu_percent,
                    'cpu_percents': cpu_percents,
                    'cpu_freq': cpu_freq_text,
                    'memory_percent': memory_percent,
                    'memory_used_gb': memory_used_gb,
                    'memory_total_gb': memory_total_gb,
                    'memory_available_gb': memory_available_gb,
                    'memory_cached_gb': memory_cached_gb,
                    'memory_breakdown': memory_breakdown,
                    'disk_partitions': disk_partitions,
                    'disk_read_rate': disk_read_rate,
                    'disk_write_rate': disk_write_rate,
                    'net_sent_rate': net_sent_rate,
                    'net_recv_rate': net_recv_rate,
                    'cpu_history': self.cpu_history.copy(),
                    'memory_history': self.memory_history.copy(),
                    'disk_io_history': self.disk_io_history.copy(),
                    'net_io_history': self.net_io_history.copy(),
                    'timestamp': current_time
                })
                
                # Sleep for refresh rate
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"Error updating data: {str(e)}")
                time.sleep(1)
    
    def get_update(self):
        """Get the latest update from the queue"""
        if not self.update_queue.empty():
            return self.update_queue.get()
        return None
    
    def set_update_interval(self, interval):
        """Set the update interval in seconds"""
        try:
            self.update_interval = float(interval)
        except ValueError:
            self.update_interval = 1.0