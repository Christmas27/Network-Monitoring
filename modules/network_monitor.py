#!/usr/bin/env python3
"""
Network Monitor Module - Real Lab Implementation

Provides real-time monitoring, health checks, and alerting for network devices.
Enhanced with Docker container monitoring and SSH performance tracking.
"""

import json
import logging
import time
import threading
import subprocess
import docker
import psutil
import paramiko
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import sqlite3
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import ping3

logger = logging.getLogger(__name__)

@dataclass
class Alert:
    """Network alert data structure"""
    id: str
    device_id: str
    alert_type: str
    severity: str
    message: str
    timestamp: datetime
    acknowledged: bool = False

@dataclass  
class DeviceMetrics:
    """Device performance metrics"""
    device_id: str
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_latency: float
    ssh_response_time: float
    status: str

class NetworkMonitor:
    """
    Network monitoring and health check system with real Docker lab integration
    
    Features:
    - Real-time Docker container monitoring
    - SSH performance metrics
    - Network latency tracking
    - Alerting system
    - Historical data collection
    """
    
    def __init__(self, config_file: str = "config.json"):
        self.config = self._load_config(config_file)
        self.db_path = "data/monitoring.db"
        self.alerts = []
        self.metrics_cache = {}
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Initialize Docker client
        try:
            self.docker_client = docker.from_env()
            logger.info("🐳 Docker client initialized for container monitoring")
        except Exception as e:
            logger.warning(f"⚠️ Docker client not available: {e}")
            self.docker_client = None
        self._init_database()
        
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get('monitoring', {})
        except FileNotFoundError:
            logger.warning(f"Config file {config_file} not found, using defaults")
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """Return default monitoring configuration"""
        return {
            "ping_interval": 30,
            "alert_thresholds": {
                "cpu_usage": 80,
                "memory_usage": 85,
                "response_time": 5000
            }
        }
    
    def _init_database(self):
        """Initialize enhanced monitoring database with real metrics support"""
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # Enhanced device metrics table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS device_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    container_id TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT NOT NULL,
                    cpu_usage REAL,
                    memory_usage REAL,
                    memory_limit REAL,
                    disk_usage REAL,
                    network_rx_bytes REAL,
                    network_tx_bytes REAL,
                    ssh_response_time REAL,
                    ping_response_time REAL,
                    uptime_seconds REAL
                )
            ''')
            
            # Network performance history
            conn.execute('''
                CREATE TABLE IF NOT EXISTS network_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    latency_ms REAL,
                    packet_loss REAL,
                    bandwidth_mbps REAL,
                    jitter_ms REAL
                )
            ''')
            
            # Enhanced alerts table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    acknowledged BOOLEAN DEFAULT FALSE,
                    resolved_timestamp TIMESTAMP NULL
                )
            ''')
            
            # System health summary
            conn.execute('''
                CREATE TABLE IF NOT EXISTS system_health (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_devices INTEGER,
                    active_devices INTEGER,
                    critical_alerts INTEGER,
                    warning_alerts INTEGER,
                    average_response_time REAL,
                    system_load REAL
                )
            ''')
            
            conn.commit()
            logger.info("📊 Enhanced monitoring database initialized")
    
    def get_lab_containers(self) -> List[Dict[str, Any]]:
        """Get information about lab containers"""
        containers = []
        if not self.docker_client:
            return containers
            
        try:
            for container in self.docker_client.containers.list():
                if container.name.startswith('lab-'):
                    container_info = {
                        'id': container.id,
                        'name': container.name,
                        'status': container.status,
                        'created': container.attrs['Created'],
                        'ports': container.ports
                    }
                    containers.append(container_info)
        except Exception as e:
            logger.error(f"❌ Error getting lab containers: {e}")
            
        return containers
    
    def get_container_metrics(self, container_name: str) -> Dict[str, Any]:
        """Get real-time metrics from Docker container"""
        if not self.docker_client:
            return {'status': 'docker_unavailable'}
            
        try:
            container = self.docker_client.containers.get(container_name)
            stats = container.stats(stream=False)
            
            # Calculate CPU usage - handle missing percpu_usage gracefully
            try:
                cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                           stats['precpu_stats']['cpu_usage']['total_usage']
                system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                              stats['precpu_stats']['system_cpu_usage']
                
                # Get number of CPUs - fallback if percpu_usage not available
                num_cpus = len(stats['cpu_stats']['cpu_usage'].get('percpu_usage', [1]))
                if num_cpus == 0:
                    num_cpus = 1  # Fallback to 1 CPU
                
                cpu_usage = (cpu_delta / system_delta) * num_cpus * 100.0 if system_delta > 0 else 0
            except (KeyError, ZeroDivisionError):
                cpu_usage = 0
            
            # Calculate memory usage
            try:
                memory_usage = stats['memory_stats']['usage']
                memory_limit = stats['memory_stats']['limit']
                memory_percent = (memory_usage / memory_limit) * 100.0
            except (KeyError, ZeroDivisionError):
                memory_usage = 0
                memory_limit = 0
                memory_percent = 0
            
            # Network I/O
            networks = stats.get('networks', {})
            rx_bytes = sum(net.get('rx_bytes', 0) for net in networks.values())
            tx_bytes = sum(net.get('tx_bytes', 0) for net in networks.values())
            
            # Container uptime
            try:
                created_time = container.attrs['Created']
                # Handle different datetime formats
                if 'T' in created_time:
                    if created_time.endswith('Z'):
                        created_time = created_time.replace('Z', '+00:00')
                    created_dt = datetime.fromisoformat(created_time.replace('T', ' '))
                else:
                    created_dt = datetime.fromisoformat(created_time)
                uptime = (datetime.now() - created_dt.replace(tzinfo=None)).total_seconds()
            except:
                uptime = 0
            
            metrics = {
                'status': container.status,
                'cpu_usage': round(max(0, cpu_usage), 2),
                'memory_usage': round(max(0, memory_percent), 2),
                'memory_bytes': memory_usage,
                'memory_limit': memory_limit,
                'network_rx_bytes': rx_bytes,
                'network_tx_bytes': tx_bytes,
                'uptime': uptime
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error getting metrics for {container_name}: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def test_ssh_response_time(self, host: str, port: int = 22, username: str = 'admin', password: str = 'admin') -> Dict[str, Any]:
        """Test SSH connection response time"""
        start_time = time.time()
        
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            ssh.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                timeout=5,
                auth_timeout=3
            )
            
            # Test command execution time
            exec_start = time.time()
            stdin, stdout, stderr = ssh.exec_command('echo "test"')
            stdout.read()
            exec_time = (time.time() - exec_start) * 1000
            
            ssh.close()
            
            total_time = (time.time() - start_time) * 1000
            
            return {
                'status': 'success',
                'connection_time_ms': round(total_time, 2),
                'command_execution_time_ms': round(exec_time, 2),
                'message': 'SSH connection successful'
            }
            
        except paramiko.AuthenticationException:
            # Auth failed but connection works
            total_time = (time.time() - start_time) * 1000
            return {
                'status': 'auth_failed',
                'connection_time_ms': round(total_time, 2),
                'message': 'SSH responding (auth expected to fail in lab)'
            }
        except Exception as e:
            total_time = (time.time() - start_time) * 1000
            return {
                'status': 'failed',
                'connection_time_ms': round(total_time, 2),
                'message': f'SSH failed: {str(e)}'
            }
    
    def collect_device_metrics(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """Collect comprehensive metrics for a lab device"""
        device_name = device_info.get('hostname', device_info.get('name', 'unknown'))
        ip_address = device_info.get('ip_address', '')
        
        # Parse host and port
        if ':' in ip_address:
            host, port = ip_address.split(':')
            port = int(port)
        else:
            host = ip_address
            port = 22
        
        metrics = {
            'device_id': device_name,
            'timestamp': datetime.now(),
            'status': 'unknown'
        }
        
        # Get container metrics if it's a lab device
        if device_name.startswith('lab-'):
            container_metrics = self.get_container_metrics(device_name)
            metrics.update(container_metrics)
        
        # Test SSH response time
        ssh_metrics = self.test_ssh_response_time(host, port)
        metrics['ssh_response_time'] = ssh_metrics.get('connection_time_ms', 0)
        metrics['ssh_status'] = ssh_metrics.get('status', 'failed')
        
        # Test ping response time
        ping_time = self.get_device_response_time(host)
        metrics['ping_response_time'] = ping_time if ping_time else 0
        
        # Determine overall status
        if ssh_metrics.get('status') in ['success', 'auth_failed']:
            metrics['status'] = 'active'
        else:
            metrics['status'] = 'inactive'
        
        return metrics
    
    def store_metrics(self, metrics: Dict[str, Any]):
        """Store metrics in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO device_metrics (
                        device_id, timestamp, status, cpu_usage, memory_usage,
                        ssh_response_time, ping_response_time
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metrics.get('device_id'),
                    metrics.get('timestamp'),
                    metrics.get('status'),
                    metrics.get('cpu_usage'),
                    metrics.get('memory_usage'),
                    metrics.get('ssh_response_time'),
                    metrics.get('ping_response_time')
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"❌ Error storing metrics: {e}")
    
    def get_recent_metrics(self, device_id: str = None, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent metrics for devices"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if device_id:
                    query = '''
                        SELECT * FROM device_metrics 
                        WHERE device_id = ? AND timestamp > datetime('now', '-{} hours')
                        ORDER BY timestamp DESC
                    '''.format(hours)
                    cursor = conn.execute(query, (device_id,))
                else:
                    query = '''
                        SELECT * FROM device_metrics 
                        WHERE timestamp > datetime('now', '-{} hours')
                        ORDER BY timestamp DESC
                    '''.format(hours)
                    cursor = conn.execute(query)
                
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"❌ Error getting recent metrics: {e}")
            return []
    
    def ping_device(self, ip_address: str) -> bool:
        """
        Ping device to check connectivity
        
        Args:
            ip_address: Device IP address
            
        Returns:
            bool: True if device is reachable
        """
        try:
            response_time = ping3.ping(ip_address, timeout=3)
            return response_time is not None
        except Exception as e:
            logger.debug(f"Ping failed for {ip_address}: {e}")
            return False
    
    def get_device_response_time(self, ip_address: str) -> Optional[float]:
        """
        Get device response time in milliseconds
        
        Args:
            ip_address: Device IP address
            
        Returns:
            float: Response time in ms or None if unreachable
        """
        try:
            response_time = ping3.ping(ip_address, timeout=5)
            if response_time is not None:
                return response_time * 1000  # Convert to milliseconds
            return None
        except Exception as e:
            logger.debug(f"Response time check failed for {ip_address}: {e}")
            return None
    
    def check_port_connectivity(self, ip_address: str, port: int, timeout: int = 5) -> bool:
        """
        Check if specific port is open on device
        
        Args:
            ip_address: Device IP address
            port: Port number
            timeout: Connection timeout
            
        Returns:
            bool: True if port is open
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((ip_address, port))
                return result == 0
        except Exception as e:
            logger.debug(f"Port check failed for {ip_address}:{port}: {e}")
            return False
    
    def get_device_status(self, device_id: str, device_info: Dict = None) -> Dict:
        """
        Get comprehensive device status
        
        Args:
            device_id: Device ID
            device_info: Device information dict (optional)
            
        Returns:
            Dict: Device status information
        """
        if not device_info:
            # If no device info provided, create basic structure
            device_info = {
                'hostname': f'Device-{device_id}',
                'ip_address': '192.168.1.1',
                'port': 22
            }
        
        status = {
            "device_id": device_id,
            "hostname": device_info.get('hostname', 'Unknown'),
            "ip_address": device_info.get('ip_address', ''),
            "timestamp": datetime.now().isoformat(),
            "ping_status": "unknown",
            "ssh_status": "unknown",
            "response_time": None
        }
        
        try:
            ip_address = device_info.get('ip_address')
            if not ip_address:
                status["error"] = "No IP address configured"
                return status
            
            # Check ping connectivity
            ping_success = self.ping_device(ip_address)
            status["ping_status"] = "online" if ping_success else "offline"
            
            if ping_success:
                # Get response time
                response_time = self.get_device_response_time(ip_address)
                if response_time:
                    status["response_time"] = round(response_time, 2)
                
                # Check SSH connectivity
                ssh_port = device_info.get('port', 22)
                ssh_available = self.check_port_connectivity(ip_address, ssh_port)
                status["ssh_status"] = "available" if ssh_available else "unavailable"
            
            # Store status in database
            self._store_device_status(device_id, status)
            
        except Exception as e:
            logger.error(f"Error getting device status for {device_id}: {e}")
            status["error"] = str(e)
        
        return status
    
    def _store_device_status(self, device_id: str, status: Dict):
        """Store device status in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO device_status (
                        device_id, status, response_time
                    ) VALUES (?, ?, ?)
                ''', (
                    device_id,
                    status.get('ping_status', 'unknown'),
                    status.get('response_time')
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error storing device status: {e}")
    
    def get_network_metrics(self) -> Dict:
        """Get aggregated network metrics"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "total_devices": 0,
            "online_devices": 0,
            "offline_devices": 0,
            "average_response_time": 0,
            "alerts_count": len(self.alerts)
        }
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get recent device status
                cursor = conn.execute('''
                    SELECT status, response_time
                    FROM device_status 
                    WHERE timestamp > datetime('now', '-5 minutes')
                ''')
                
                statuses = cursor.fetchall()
                if statuses:
                    online_count = sum(1 for s in statuses if s[0] == 'online')
                    total_count = len(statuses)
                    
                    metrics["total_devices"] = total_count
                    metrics["online_devices"] = online_count
                    metrics["offline_devices"] = total_count - online_count
                    
                    # Calculate average response time
                    response_times = [s[1] for s in statuses if s[1] is not None]
                    if response_times:
                        metrics["average_response_time"] = round(sum(response_times) / len(response_times), 2)
        
        except Exception as e:
            logger.error(f"Error getting network metrics: {e}")
        
        return metrics
    
    def check_alerts(self, devices: List[Dict] = None) -> List[Alert]:
        """Check for new alerts based on current metrics"""
        if not devices:
            devices = []
        
        new_alerts = []
        thresholds = self.config.get('alert_thresholds', {})
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check for offline devices
                cursor = conn.execute('''
                    SELECT DISTINCT device_id
                    FROM device_status 
                    WHERE timestamp > datetime('now', '-10 minutes')
                    AND status = 'offline'
                ''')
                
                for (device_id,) in cursor.fetchall():
                    alert = Alert(
                        id=f"offline_{device_id}_{int(time.time())}",
                        device_id=device_id,
                        alert_type="device_offline",
                        severity="critical",
                        message="Device is offline",
                        timestamp=datetime.now()
                    )
                    new_alerts.append(alert)
                    
                # Check for high response times
                if 'response_time' in thresholds:
                    cursor = conn.execute('''
                        SELECT DISTINCT device_id, response_time
                        FROM device_status 
                        WHERE timestamp > datetime('now', '-5 minutes')
                        AND response_time > ?
                    ''', (thresholds['response_time'],))
                    
                    for device_id, response_time in cursor.fetchall():
                        alert = Alert(
                            id=f"latency_{device_id}_{int(time.time())}",
                            device_id=device_id,
                            alert_type="high_latency",
                            severity="warning",
                            message=f"High response time: {response_time}ms",
                            timestamp=datetime.now()
                        )
                        new_alerts.append(alert)
        
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
        
        # Store new alerts
        for alert in new_alerts:
            self._store_alert(alert)
        
        return new_alerts
    
    def _store_alert(self, alert: Alert):
        """Store alert in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO alerts (
                        id, device_id, alert_type, severity, message, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    alert.id,
                    alert.device_id,
                    alert.alert_type,
                    alert.severity,
                    alert.message,
                    alert.timestamp.isoformat()
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error storing alert: {e}")
    
    def get_alerts(self, limit: int = 50) -> List[Dict]:
        """Get recent alerts"""
        alerts = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT * FROM alerts 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
                
                for row in cursor.fetchall():
                    alerts.append(dict(row))
        
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
        
        return alerts
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str = "system") -> bool:
        """Acknowledge an alert"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE alerts 
                    SET acknowledged = TRUE
                    WHERE id = ?
                ''', (alert_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error acknowledging alert {alert_id}: {e}")
            return False
    
    def get_network_topology(self) -> Dict:
        """Get network topology (simplified implementation)"""
        try:
            # Try to get real data from Catalyst Center if available
            try:
                from modules.catalyst_center_integration import CatalystCenterManager
                catalyst_manager = CatalystCenterManager()
                
                test_result = catalyst_manager.test_connection()
                if test_result.get('status') == 'success':
                    return self._get_catalyst_center_topology(catalyst_manager)
            except ImportError:
                logger.debug("Catalyst Center module not available")
            except Exception as e:
                logger.debug(f"Catalyst Center connection failed: {e}")
            
            # Fallback to simulation
            return self._get_simulation_topology()
                
        except Exception as e:
            logger.error(f"Error getting topology: {e}")
            return self._get_simulation_topology()

    def _get_catalyst_center_topology(self, catalyst_manager):
        """Get topology from Catalyst Center"""
        try:
            devices = catalyst_manager.get_device_inventory()
            
            nodes = []
            for device in devices:
                node = {
                    'id': device['id'],
                    'label': f"{device['name']}\n{device['host']}",
                    'type': self._map_device_type(device.get('type', 'switch')),
                    'status': device.get('status', 'unknown'),
                    'ip': device['host'],
                    'model': device.get('description', 'Cisco Device'),
                    'hostname': device['name']
                }
                nodes.append(node)
            
            # Create logical connections
            edges = self._create_logical_topology(nodes)
            
            online_devices = len([d for d in devices if d.get('status') == 'online'])
            total_devices = len(devices)
            
            stats = {
                'totalDevices': total_devices,
                'onlineDevices': online_devices,
                'totalConnections': len(edges),
                'networkHealth': f"{round((online_devices / total_devices * 100) if total_devices > 0 else 0)}%" 
            }
            
            return {
                'status': 'catalyst_center',
                'nodes': nodes,
                'edges': edges,
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"Error processing Catalyst Center topology: {e}")
            return self._get_simulation_topology()

    def _map_device_type(self, device_type):
        """Map device types to topology types"""
        device_type_lower = device_type.lower() if device_type else ''
        
        if 'switch' in device_type_lower or 'catalyst' in device_type_lower:
            return 'switch'
        elif 'router' in device_type_lower or 'isr' in device_type_lower:
            return 'router'
        elif 'access point' in device_type_lower or 'ap' in device_type_lower:
            return 'access_point'
        elif 'wireless' in device_type_lower or 'wlc' in device_type_lower:
            return 'wireless_controller'
        elif 'firewall' in device_type_lower or 'asa' in device_type_lower:
            return 'firewall'
        else:
            return 'switch'

    def _create_logical_topology(self, nodes):
        """Create logical network topology"""
        edges = []
        
        # Group devices by type
        routers = [n for n in nodes if n['type'] == 'router']
        switches = [n for n in nodes if n['type'] == 'switch']
        
        # Connect routers to switches
        for router in routers:
            for switch in switches[:2]:  # Connect to first 2 switches
                edges.append({
                    'from': router['id'],
                    'to': switch['id'],
                    'status': 'active'
                })
        
        # Connect switches to each other
        for i, switch1 in enumerate(switches):
            for switch2 in switches[i+1:]:
                edges.append({
                    'from': switch1['id'],
                    'to': switch2['id'],
                    'status': 'active'
                })
        
        return edges

    def _get_simulation_topology(self):
        """Fallback simulation topology"""
        return {
            'status': 'simulation',
            'nodes': [
                { 
                    'id': 'sim-router-1', 
                    'label': 'Demo Router\n192.168.1.1', 
                    'type': 'router', 
                    'status': 'online', 
                    'ip': '192.168.1.1',
                    'model': 'Cisco ISR 4431 (Demo)',
                    'hostname': 'Demo-Router'
                },
                { 
                    'id': 'sim-switch-1', 
                    'label': 'Demo Switch\n192.168.1.10', 
                    'type': 'switch', 
                    'status': 'online', 
                    'ip': '192.168.1.10',
                    'model': 'Cisco Catalyst 9300 (Demo)',
                    'hostname': 'Demo-Switch'
                }
            ],
            'edges': [
                { 'from': 'sim-router-1', 'to': 'sim-switch-1', 'status': 'active' }
            ],
            'stats': {
                'totalDevices': 2,
                'onlineDevices': 2,
                'totalConnections': 1,
                'networkHealth': '100%'
            }
        }
    
    def start_monitoring(self, devices: List[Dict] = None):
        """Start background monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, 
            args=(devices or [],), 
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("Network monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Network monitoring stopped")
    
    def _monitoring_loop(self, devices):
        """Main monitoring loop"""
        interval = self.config.get('ping_interval', 30)
        
        while self.monitoring_active:
            try:
                if devices:
                    # Monitor devices in parallel
                    with ThreadPoolExecutor(max_workers=5) as executor:
                        futures = {executor.submit(self.get_device_status, device['id'], device): device['id'] 
                                 for device in devices}
                        
                        for future in as_completed(futures):
                            device_id = futures[future]
                            try:
                                status = future.result()
                                self.metrics_cache[device_id] = status
                            except Exception as e:
                                logger.error(f"Error monitoring device {device_id}: {e}")
                    
                    # Check for alerts
                    self.check_alerts(devices)
                
                logger.debug(f"Monitoring cycle completed for {len(devices)} devices")
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            
            # Wait for next interval
            time.sleep(interval)
    
    def cleanup_old_data(self):
        """Clean up old monitoring data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Keep only last 7 days of status data
                conn.execute('''
                    DELETE FROM device_status 
                    WHERE timestamp < datetime('now', '-7 days')
                ''')
                
                # Keep only last 30 days of alerts
                conn.execute('''
                    DELETE FROM alerts 
                    WHERE timestamp < datetime('now', '-30 days')
                ''')
                
                conn.commit()
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
