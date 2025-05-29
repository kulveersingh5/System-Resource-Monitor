import psutil
import platform
import threading
import time
import subprocess
import queue
from datetime import datetime

class SystemMonitor:
    def __init__(self, update_interval=1.0):
        # Data storage for charts
        self.cpu_history = [0] * 30
        self.memory_history = [0] * 30
        self.disk_history = [0] * 30
        self.network_history = [0] * 30
        
        # Previous values for rate calculations
        self.prev_disk_read = 0
        self.prev_disk_write = 0
        self.prev_net_sent = 0
        self.prev_net_recv = 0
        self.prev_time = time.time()
        
        # Thread-safe queues
        self.update_queue = queue.Queue() # stores system resource data
        self.command_queue = queue.Queue() #stores commands to execute
        self.command_result_queue = queue.Queue() #result of the executed commands for gui
        
        self.update_interval = update_interval
        self.running = True
        self.update_thread = None
        
        self.commands = {
            'Ping': ['ping', '-n', '4', 'google.com'],
            'IP Config': ['ipconfig'],
            'Task List': ['tasklist'],
            'System Info': ['systeminfo'],
            'Hostname': ['hostname'],
            'Echo Hello': ['echo', 'hello']
        }
    
    def start(self):
        """Start monitoring"""
        self.running = True
        self.update_thread = threading.Thread(target=self.update_data, daemon=True)
        self.update_thread.start()
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1.0)
    
    def get_cpu_info(self):
        """Get CPU information"""
        try:
            cpu_freq = psutil.cpu_freq()
            return {
                'cpu_count': psutil.cpu_count(logical=True),
                'physical_cores': psutil.cpu_count(logical=False),
                'current_freq': cpu_freq.current if cpu_freq else 0,
                'max_freq': cpu_freq.max if cpu_freq else 0,
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'per_cpu': psutil.cpu_percent(interval=0.1, percpu=True)
            }
        except:
            return {'cpu_count': 1, 'physical_cores': 1, 'current_freq': 0, 'max_freq': 0, 'cpu_percent': 0, 'per_cpu': [0]}
    
    def get_memory_info(self):
        """Get memory information"""
        try:
            memory = psutil.virtual_memory()
            return {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent,
                'total_gb': memory.total / (1024**3),
                'available_gb': memory.available / (1024**3),
                'used_gb': memory.used / (1024**3)
            }
        except:
            return {'total': 0, 'available': 0, 'used': 0, 'percent': 0, 'total_gb': 0, 'available_gb': 0, 'used_gb': 0}
    
    def get_disk_info(self):
        """Get disk information"""
        disks = []
        try:
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent,
                        'total_gb': usage.total / (1024**3),
                        'used_gb': usage.used / (1024**3),
                        'free_gb': usage.free / (1024**3)
                    })
                except PermissionError:
                    pass
        except:
            pass
        
        # Get disk I/O
        try:
            disk_io = psutil.disk_io_counters()
            io_info = {
                'read_bytes': disk_io.read_bytes if disk_io else 0,
                'write_bytes': disk_io.write_bytes if disk_io else 0,
                'read_count': disk_io.read_count if disk_io else 0,
                'write_count': disk_io.write_count if disk_io else 0
            }
        except:
            io_info = {'read_bytes': 0, 'write_bytes': 0, 'read_count': 0, 'write_count': 0}
        
        return {'partitions': disks, 'io': io_info}
    
    def get_network_info(self):
        """Get network information"""
        try:
            # Network I/O
            net_io = psutil.net_io_counters()
            io_info = {
                'bytes_sent': net_io.bytes_sent if net_io else 0,
                'bytes_recv': net_io.bytes_recv if net_io else 0,
                'packets_sent': net_io.packets_sent if net_io else 0,
                'packets_recv': net_io.packets_recv if net_io else 0
            }
            
            # Network interfaces
            interfaces = []
            for interface, addrs in psutil.net_if_addrs().items():
                addresses = []
                for addr in addrs:
                    if addr.family.name == 'AF_INET':
                        addresses.append({'type': 'IPv4', 'address': addr.address})
                    elif addr.family.name == 'AF_INET6':
                        addresses.append({'type': 'IPv6', 'address': addr.address})
                
                # Get interface stats
                stats = psutil.net_if_stats().get(interface)
                interfaces.append({
                    'name': interface,
                    'addresses': addresses,
                    'is_up': stats.isup if stats else False,
                    'speed': stats.speed if stats else 0
                })
            
            return {'io': io_info, 'interfaces': interfaces}
        except:
            return {'io': {'bytes_sent': 0, 'bytes_recv': 0, 'packets_sent': 0, 'packets_recv': 0}, 'interfaces': []}
    
    def get_processes(self):
        """Get process information"""
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    pinfo = proc.info
                    processes.append({
                        'pid': pinfo['pid'],
                        'name': pinfo['name'][:40],
                        'cpu_percent': pinfo['cpu_percent'] or 0,
                        'memory_percent': pinfo['memory_percent'] or 0,
                        'status': pinfo['status']
                    })
                except:
                    pass
        except:
            pass
        return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:100]
    
    def execute_command(self, command_name):
        """Execute a command"""
        if command_name not in self.commands:
            return {'success': False, 'output': 'Command not found'}
        
        try:
            cmd = self.commands[command_name]
            
            # Set timeout based on command type
            timeout = 30 if command_name == 'System Info' else 15
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=True)
            
            if result.returncode == 0:
                return {'success': True, 'output': result.stdout}
            else:
                return {'success': False, 'output': result.stderr or 'Command failed'}
        except subprocess.TimeoutExpired:
            return {'success': False, 'output': f'Command timeout ({timeout} seconds)'}
        except Exception as e:
            return {'success': False, 'output': f'Error: {str(e)}'}
    
    def kill_process(self, pid):
        """Kill a process"""
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            return {'success': True, 'message': f'Process {pid} terminated'}
        except psutil.NoSuchProcess:
            return {'success': False, 'message': 'Process not found'}
        except psutil.AccessDenied:
            return {'success': False, 'message': 'Access denied'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def update_data(self):
        """Background data collection"""
        while self.running:
            try:
                current_time = time.time()
                time_diff = current_time - self.prev_time
                
                # Get all system data
                cpu_info = self.get_cpu_info()
                memory_info = self.get_memory_info()
                disk_info = self.get_disk_info()
                network_info = self.get_network_info()
                
                # Calculate rates
                disk_rate = 0
                network_rate = 0
                
                if time_diff > 0:
                    # Disk rate (MB/s)
                    disk_read_rate = (disk_info['io']['read_bytes'] - self.prev_disk_read) / time_diff / (1024**2)
                    disk_write_rate = (disk_info['io']['write_bytes'] - self.prev_disk_write) / time_diff / (1024**2)
                    disk_rate = disk_read_rate + disk_write_rate
                    
                    # Network rate (KB/s)
                    net_sent_rate = (network_info['io']['bytes_sent'] - self.prev_net_sent) / time_diff / 1024
                    net_recv_rate = (network_info['io']['bytes_recv'] - self.prev_net_recv) / time_diff / 1024
                    network_rate = net_sent_rate + net_recv_rate
                    
                    self.prev_disk_read = disk_info['io']['read_bytes']
                    self.prev_disk_write = disk_info['io']['write_bytes']
                    self.prev_net_sent = network_info['io']['bytes_sent']
                    self.prev_net_recv = network_info['io']['bytes_recv']
                
                # Update history
                self.cpu_history.append(cpu_info['cpu_percent'])
                self.cpu_history.pop(0)
                self.memory_history.append(memory_info['percent'])
                self.memory_history.pop(0)
                self.disk_history.append(min(disk_rate, 100))  # Cap at 100 for chart
                self.disk_history.pop(0)
                self.network_history.append(min(network_rate, 1000))  # Cap at 1000 for chart
                self.network_history.pop(0)
                
                self.prev_time = current_time
                
                # Put data in queue
                self.update_queue.put({
                    'cpu': cpu_info,
                    'memory': memory_info,
                    'disk': disk_info,
                    'network': network_info,
                    'cpu_history': self.cpu_history.copy(),
                    'memory_history': self.memory_history.copy(),
                    'disk_history': self.disk_history.copy(),
                    'network_history': self.network_history.copy(),
                    'disk_rate': disk_rate,
                    'network_rate': network_rate
                })
                
                # Process commands
                if not self.command_queue.empty():
                    try:
                        command_type, data = self.command_queue.get_nowait()
                        if command_type == 'execute':
                            result = self.execute_command(data)
                            self.command_result_queue.put(('command_result', result))
                        elif command_type == 'kill_process':
                            result = self.kill_process(data)
                            self.command_result_queue.put(('kill_result', result))
                    except queue.Empty:
                        pass
                
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"Error in update: {e}")
                time.sleep(1)
    
    def get_update(self):
        """Get latest data"""
        try:
            return self.update_queue.get_nowait()
        except queue.Empty:
            return None
    
    def get_command_result(self):
        """Get command result"""
        try:
            return self.command_result_queue.get_nowait()
        except queue.Empty:
            return None
    
    def get_commands(self):
        """Get available commands"""
        return list(self.commands.keys())

if __name__ == "__main__":
    print("System Monitor Backend - Testing...")
    monitor = SystemMonitor()
    
    # Test all components
    print("CPU Info:", monitor.get_cpu_info())
    print("Memory Info:", monitor.get_memory_info())
    print("Commands:", monitor.get_commands())
    
    print("Backend test completed!")