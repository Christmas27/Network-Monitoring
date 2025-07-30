#!/usr/bin/env python3
"""
Network Monitor Module

Provides real-time monitoring, health checks, and alerting for network devices.
Demonstrates network monitoring best practices and automation.
"""

import json
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import sqlite3
import subprocess
import platform
from concurrent.futures import ThreadPoolExecutor, as_completed
import socket
import requests
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

class NetworkMonitor:
    """
    Network monitoring and health check system
    
    Features:
    - Real-time device status monitoring
    - Performance metrics collection
    - Alerting and notification system
    - Network topology discovery
    - SNMP monitoring support
    """
    
    def __init__(self, config_file: str = "config.json"):
        self.config = self._load_config(config_file)
        self.db_path = "data/monitoring.db"
        self.alerts = []
        self.metrics_cache = {}
        self.monitoring_active = False
        self.monitor_thread = None
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
            "snmp_timeout": 10,
            "ssh_timeout": 15,
            "alert_thresholds": {
                "cpu_usage": 80,
                "memory_usage": 85,
                "interface_errors": 100,
                "response_time": 5000
            }
        }
    
    def _init_database(self):
        """Initialize monitoring database"""
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # Device status history
            conn.execute('''
                CREATE TABLE IF NOT EXISTS device_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT NOT NULL,
                    response_time REAL,
                    cpu_usage REAL,
                    memory_usage REAL,
                    uptime INTEGER
                )
            ''')
            
            # Interface statistics
            conn.execute('''
                CREATE TABLE IF NOT EXISTS interface_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    interface_name TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    bytes_in BIGINT,
                    bytes_out BIGINT,
                    packets_in BIGINT,
                    packets_out BIGINT,
                    errors_in INTEGER,
                    errors_out INTEGER,
                    utilization REAL
                )
            ''')
            
            # Alerts history
            conn.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    device_id TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    acknowledged BOOLEAN DEFAULT FALSE,
                    acknowledged_by TEXT,
                    acknowledged_at TIMESTAMP
                )
            ''')
            
            # Network topology
            conn.execute('''
                CREATE TABLE IF NOT EXISTS topology_links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_device TEXT NOT NULL,
                    target_device TEXT NOT NULL,
                    source_interface TEXT,
                    target_interface TEXT,
                    link_type TEXT,
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.info("Monitoring database initialized")
    
    def ping_device(self, ip_address: str) -> bool:
        """
        Ping device to check connectivity
        
        Args:
            ip_address: Device IP address
            
        Returns:
            bool: True if device is reachable
        """
        try:
            # Use ping3 for cross-platform compatibility
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
    
    def get_device_status(self, device_id: str) -> Dict:
        """
        Get comprehensive device status
        
        Args:
            device_id: Device ID
            
        Returns:
            Dict: Device status information
        """
        # Import here to avoid circular imports
        from .device_manager import DeviceManager
        
        device_manager = DeviceManager()
        device = device_manager.get_device(device_id)
        
        if not device:
            return {"error": "Device not found"}
        
        status = {
            "device_id": device_id,
            "hostname": device['hostname'],
            "ip_address": device['ip_address'],
            "timestamp": datetime.now().isoformat(),
            "ping_status": "unknown",
            "ssh_status": "unknown",
            "response_time": None,
            "uptime": None,
            "cpu_usage": None,
            "memory_usage": None
        }
        
        try:
            # Check ping connectivity
            ping_success = self.ping_device(device['ip_address'])
            status["ping_status"] = "online" if ping_success else "offline"
            
            if ping_success:
                # Get response time
                response_time = self.get_device_response_time(device['ip_address'])
                if response_time:
                    status["response_time"] = round(response_time, 2)
                
                # Check SSH connectivity
                ssh_port = device.get('port', 22)
                ssh_available = self.check_port_connectivity(device['ip_address'], ssh_port)
                status["ssh_status"] = "available" if ssh_available else "unavailable"
                
                # Try to get detailed metrics via SSH
                if ssh_available:
                    detailed_metrics = self._get_device_metrics_ssh(device_id)
                    status.update(detailed_metrics)
            
            # Store status in database
            self._store_device_status(device_id, status)
            
        except Exception as e:
            logger.error(f"Error getting device status for {device_id}: {e}")
            status["error"] = str(e)
        
        return status
    
    def _get_device_metrics_ssh(self, device_id: str) -> Dict:
        """Get detailed device metrics via SSH"""
        from .device_manager import DeviceManager
        
        metrics = {}
        device_manager = DeviceManager()
        
        try:
            connection = device_manager.connect_to_device(device_id)
            if not connection:
                return metrics
            
            device = device_manager.get_device(device_id)
            device_type = device['device_type'].lower()
            
            if 'cisco' in device_type:
                metrics.update(self._parse_cisco_metrics(connection))
            elif 'juniper' in device_type:
                metrics.update(self._parse_juniper_metrics(connection))
            elif 'arista' in device_type:
                metrics.update(self._parse_arista_metrics(connection))
            
        except Exception as e:
            logger.error(f"Error getting SSH metrics for {device_id}: {e}")
        
        return metrics
    
    def _parse_cisco_metrics(self, connection) -> Dict:
        """Parse Cisco device metrics"""
        metrics = {}
        
        try:
            # Get CPU usage
            cpu_output = connection.send_command("show processes cpu")
            cpu_lines = cpu_output.split('\n')
            for line in cpu_lines:
                if 'five minutes:' in line.lower():
                    # Extract 5-minute CPU average
                    parts = line.split('five minutes:')
                    if len(parts) > 1:
                        cpu_str = parts[1].split('%')[0].strip()
                        try:
                            metrics['cpu_usage'] = float(cpu_str)
                        except ValueError:
                            pass
                    break
            
            # Get memory usage
            memory_output = connection.send_command("show memory")
            memory_lines = memory_output.split('\n')
            for line in memory_lines:
                if 'Processor' in line and 'free' in line.lower():
                    # Parse memory information
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            total = int(parts[2])
                            free = int(parts[4])
                            used = total - free
                            metrics['memory_usage'] = round((used / total) * 100, 2)
                        except (ValueError, ZeroDivisionError):
                            pass
                    break
            
            # Get uptime
            version_output = connection.send_command("show version")
            for line in version_output.split('\n'):
                if 'uptime is' in line.lower():
                    metrics['uptime_string'] = line.strip()
                    break
            
        except Exception as e:
            logger.error(f"Error parsing Cisco metrics: {e}")
        
        return metrics
    
    def _parse_juniper_metrics(self, connection) -> Dict:
        """Parse Juniper device metrics"""
        metrics = {}
        
        try:
            # Get system information
            system_output = connection.send_command("show system uptime")
            if system_output:
                metrics['uptime_string'] = system_output.strip()
            
            # Get chassis environment
            chassis_output = connection.send_command("show chassis environment")
            # Parse CPU and temperature if available
            
        except Exception as e:
            logger.error(f"Error parsing Juniper metrics: {e}")
        
        return metrics
    
    def _parse_arista_metrics(self, connection) -> Dict:
        """Parse Arista device metrics"""
        metrics = {}
        
        try:
            # Get version and uptime
            version_output = connection.send_command("show version")
            if 'Uptime:' in version_output:
                for line in version_output.split('\n'):
                    if 'Uptime:' in line:
                        metrics['uptime_string'] = line.strip()
                        break
        
        except Exception as e:
            logger.error(f"Error parsing Arista metrics: {e}")
        
        return metrics
    
    def _store_device_status(self, device_id: str, status: Dict):
        """Store device status in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO device_status (
                    device_id, status, response_time, cpu_usage, memory_usage
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                device_id,
                status.get('ping_status', 'unknown'),
                status.get('response_time'),
                status.get('cpu_usage'),
                status.get('memory_usage')
            ))
            conn.commit()
    
    def get_network_metrics(self) -> Dict:
        """Get aggregated network metrics"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "total_devices": 0,
            "online_devices": 0,
            "offline_devices": 0,
            "average_response_time": 0,
            "alerts_count": len(self.alerts),
            "performance_summary": {}
        }
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get recent device status
                cursor = conn.execute('''
                    SELECT status, response_time, cpu_usage, memory_usage
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
                    
                    # Performance summary
                    cpu_values = [s[2] for s in statuses if s[2] is not None]
                    memory_values = [s[3] for s in statuses if s[3] is not None]
                    
                    if cpu_values:
                        metrics["performance_summary"]["avg_cpu"] = round(sum(cpu_values) / len(cpu_values), 2)
                        metrics["performance_summary"]["max_cpu"] = max(cpu_values)
                    
                    if memory_values:
                        metrics["performance_summary"]["avg_memory"] = round(sum(memory_values) / len(memory_values), 2)
                        metrics["performance_summary"]["max_memory"] = max(memory_values)
        
        except Exception as e:
            logger.error(f"Error getting network metrics: {e}")
        
        return metrics
    
    def check_alerts(self) -> List[Alert]:
        """Check for new alerts based on current metrics"""
        new_alerts = []
        thresholds = self.config.get('alert_thresholds', {})
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check for devices with high CPU usage
                if 'cpu_usage' in thresholds:
                    cursor = conn.execute('''
                        SELECT DISTINCT device_id, cpu_usage
                        FROM device_status 
                        WHERE timestamp > datetime('now', '-5 minutes')
                        AND cpu_usage > ?
                    ''', (thresholds['cpu_usage'],))
                    
                    for device_id, cpu_usage in cursor.fetchall():
                        alert = Alert(
                            id=f"cpu_{device_id}_{int(time.time())}",
                            device_id=device_id,
                            alert_type="high_cpu",
                            severity="warning",
                            message=f"High CPU usage detected: {cpu_usage}%",
                            timestamp=datetime.now()
                        )
                        new_alerts.append(alert)
                
                # Check for devices with high memory usage
                if 'memory_usage' in thresholds:
                    cursor = conn.execute('''
                        SELECT DISTINCT device_id, memory_usage
                        FROM device_status 
                        WHERE timestamp > datetime('now', '-5 minutes')
                        AND memory_usage > ?
                    ''', (thresholds['memory_usage'],))
                    
                    for device_id, memory_usage in cursor.fetchall():
                        alert = Alert(
                            id=f"memory_{device_id}_{int(time.time())}",
                            device_id=device_id,
                            alert_type="high_memory",
                            severity="warning",
                            message=f"High memory usage detected: {memory_usage}%",
                            timestamp=datetime.now()
                        )
                        new_alerts.append(alert)
                
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
        
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
        
        # Store new alerts
        for alert in new_alerts:
            self._store_alert(alert)
        
        return new_alerts
    
    def _store_alert(self, alert: Alert):
        """Store alert in database"""
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
                    SET acknowledged = TRUE, 
                        acknowledged_by = ?, 
                        acknowledged_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (acknowledged_by, alert_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error acknowledging alert {alert_id}: {e}")
            return False
    
    def get_network_topology(self) -> Dict:
        """
        Discover and return network topology
        This is a simplified implementation - in production, you'd use LLDP/CDP discovery
        """
        topology = {
            "nodes": [],
            "links": [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Import here to avoid circular imports
            from .device_manager import DeviceManager
            
            device_manager = DeviceManager()
            devices = device_manager.get_all_devices()
            
            # Add devices as nodes
            for device in devices:
                status = self.ping_device(device['ip_address'])
                node = {
                    "id": device['id'],
                    "hostname": device['hostname'],
                    "ip_address": device['ip_address'],
                    "device_type": device['device_type'],
                    "vendor": device.get('vendor', ''),
                    "status": "online" if status else "offline"
                }
                topology["nodes"].append(node)
            
            # Get topology links from database
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('SELECT * FROM topology_links')
                
                for row in cursor.fetchall():
                    link = dict(row)
                    topology["links"].append(link)
        
        except Exception as e:
            logger.error(f"Error getting network topology: {e}")
        
        return topology
    
    def start_monitoring(self):
        """Start background monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Network monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Network monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        from .device_manager import DeviceManager
        
        device_manager = DeviceManager()
        interval = self.config.get('ping_interval', 30)
        
        while self.monitoring_active:
            try:
                devices = device_manager.get_all_devices()
                
                # Monitor devices in parallel
                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = {executor.submit(self.get_device_status, device['id']): device['id'] 
                             for device in devices}
                    
                    for future in as_completed(futures):
                        device_id = futures[future]
                        try:
                            status = future.result()
                            self.metrics_cache[device_id] = status
                        except Exception as e:
                            logger.error(f"Error monitoring device {device_id}: {e}")
                
                # Check for alerts
                self.check_alerts()
                
                # Clean up old data
                self._cleanup_old_data()
                
                logger.debug(f"Monitoring cycle completed for {len(devices)} devices")
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            
            # Wait for next interval
            time.sleep(interval)
    
    def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Keep only last 7 days of status data
                conn.execute('''
                    DELETE FROM device_status 
                    WHERE timestamp < datetime('now', '-7 days')
                ''')
                
                # Keep only last 30 days of interface stats
                conn.execute('''
                    DELETE FROM interface_stats 
                    WHERE timestamp < datetime('now', '-30 days')
                ''')
                
                # Keep only last 90 days of alerts
                conn.execute('''
                    DELETE FROM alerts 
                    WHERE timestamp < datetime('now', '-90 days')
                ''')
                
                conn.commit()
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    def export_metrics(self, start_date: str, end_date: str, format: str = "json") -> str:
        """Export metrics data for specified date range"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute('''
                    SELECT * FROM device_status 
                    WHERE timestamp BETWEEN ? AND ?
                    ORDER BY timestamp
                ''', (start_date, end_date))
                
                data = [dict(row) for row in cursor.fetchall()]
                
                if format.lower() == "json":
                    return json.dumps(data, indent=2, default=str)
                elif format.lower() == "csv":
                    import csv
                    import io
                    
                    output = io.StringIO()
                    if data:
                        writer = csv.DictWriter(output, fieldnames=data[0].keys())
                        writer.writeheader()
                        writer.writerows(data)
                    
                    return output.getvalue()
        
        except Exception as e:
            logger.error(f"Error exporting metrics: {e}")
            return ""
