#!/usr/bin/env python3
"""
Device Manager Module

Handles device inventory, connection management, and basic device operations.
Demonstrates Cisco DevNet API integration and multi-vendor device support.
"""

import json
import sqlite3
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

logger = logging.getLogger(__name__)

class DeviceManager:
    """
    Manages network device inventory and connections
    
    Features:
    - Multi-vendor device support (Cisco, Juniper, Arista, etc.)
    - Secure credential management
    - Connection pooling and management
    - Device discovery and auto-inventory
    """
    
    def __init__(self, config_file: str = "config.json"):
        self.config = self._load_config(config_file)
        self.db_path = "data/devices.db"
        self.connections = {}
        self.connection_lock = threading.Lock()
        self._init_database()
        
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_file} not found, using defaults")
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """Return default configuration"""
        return {
            "device_defaults": {
                "cisco": {"port": 22, "device_type": "cisco_ios", "timeout": 15},
                "juniper": {"port": 22, "device_type": "juniper_junos", "timeout": 15},
                "arista": {"port": 22, "device_type": "arista_eos", "timeout": 15}
            }
        }
    
    def _init_database(self):
        """Initialize SQLite database for device storage"""
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS devices (
                    id TEXT PRIMARY KEY,
                    hostname TEXT NOT NULL,
                    ip_address TEXT NOT NULL UNIQUE,
                    device_type TEXT NOT NULL,
                    vendor TEXT,
                    model TEXT,
                    os_version TEXT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    enable_password TEXT,
                    port INTEGER DEFAULT 22,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_connected TIMESTAMP,
                    status TEXT DEFAULT 'unknown',
                    tags TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS device_interfaces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT,
                    interface_name TEXT,
                    ip_address TEXT,
                    subnet_mask TEXT,
                    status TEXT,
                    speed TEXT,
                    duplex TEXT,
                    description TEXT,
                    FOREIGN KEY (device_id) REFERENCES devices (id)
                )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def add_device(self, device_data: Dict) -> str:
        """
        Add a new device to the inventory
        
        Args:
            device_data: Dictionary containing device information
            
        Returns:
            str: Device ID
        """
        device_id = str(uuid.uuid4())
        
        # Validate required fields
        required_fields = ['hostname', 'ip_address', 'device_type', 'username', 'password']
        for field in required_fields:
            if field not in device_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Set defaults based on device type
        vendor = device_data.get('vendor', 'unknown')
        if vendor.lower() in self.config.get('device_defaults', {}):
            defaults = self.config['device_defaults'][vendor.lower()]
            for key, value in defaults.items():
                if key not in device_data:
                    device_data[key] = value
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO devices (
                    id, hostname, ip_address, device_type, vendor, model,
                    os_version, username, password, enable_password, port, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                device_id,
                device_data['hostname'],
                device_data['ip_address'],
                device_data['device_type'],
                device_data.get('vendor', ''),
                device_data.get('model', ''),
                device_data.get('os_version', ''),
                device_data['username'],
                device_data['password'],
                device_data.get('enable_password', ''),
                device_data.get('port', 22),
                json.dumps(device_data.get('tags', []))
            ))
            conn.commit()
        
        logger.info(f"Added device: {device_data['hostname']} ({device_data['ip_address']})")
        return device_id
    
    def get_device(self, device_id: str) -> Optional[Dict]:
        """Get device by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT * FROM devices WHERE id = ?', (device_id,))
            row = cursor.fetchone()
            
            if row:
                device = dict(row)
                device['tags'] = json.loads(device['tags'] or '[]')
                return device
            return None
    
    def get_all_devices(self) -> List[Dict]:
        """Get all devices from inventory"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT * FROM devices ORDER BY hostname')
            devices = []
            
            for row in cursor.fetchall():
                device = dict(row)
                device['tags'] = json.loads(device['tags'] or '[]')
                devices.append(device)
            
            return devices
    
    def update_device(self, device_id: str, updates: Dict) -> bool:
        """Update device information"""
        if not self.get_device(device_id):
            return False
        
        # Build update query dynamically
        update_fields = []
        values = []
        
        allowed_fields = [
            'hostname', 'ip_address', 'device_type', 'vendor', 'model',
            'os_version', 'username', 'password', 'enable_password', 'port'
        ]
        
        for field in allowed_fields:
            if field in updates:
                update_fields.append(f"{field} = ?")
                values.append(updates[field])
        
        if 'tags' in updates:
            update_fields.append("tags = ?")
            values.append(json.dumps(updates['tags']))
        
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(device_id)
        
        query = f"UPDATE devices SET {', '.join(update_fields)} WHERE id = ?"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(query, values)
            conn.commit()
        
        logger.info(f"Updated device: {device_id}")
        return True
    
    def delete_device(self, device_id: str) -> bool:
        """Delete device from inventory"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('DELETE FROM devices WHERE id = ?', (device_id,))
            if cursor.rowcount > 0:
                conn.execute('DELETE FROM device_interfaces WHERE device_id = ?', (device_id,))
                conn.commit()
                logger.info(f"Deleted device: {device_id}")
                return True
            return False
    
    def connect_to_device(self, device_id: str) -> Optional[ConnectHandler]:
        """
        Establish SSH connection to device
        
        Args:
            device_id: Device ID
            
        Returns:
            ConnectHandler: Netmiko connection object or None
        """
        device = self.get_device(device_id)
        if not device:
            logger.error(f"Device not found: {device_id}")
            return None
        
        connection_params = {
            'device_type': device['device_type'],
            'host': device['ip_address'],
            'username': device['username'],
            'password': device['password'],
            'port': device['port'],
            'timeout': 15,
            'banner_timeout': 15,
            'conn_timeout': 10,
        }
        
        if device['enable_password']:
            connection_params['secret'] = device['enable_password']
        
        try:
            with self.connection_lock:
                if device_id in self.connections:
                    # Check if existing connection is still alive
                    try:
                        self.connections[device_id].send_command('show version', expect_string=r'#')
                        return self.connections[device_id]
                    except:
                        del self.connections[device_id]
                
                # Create new connection
                connection = ConnectHandler(**connection_params)
                self.connections[device_id] = connection
                
                # Update last connected timestamp
                self.update_device(device_id, {'last_connected': datetime.now().isoformat()})
                
                logger.info(f"Connected to device: {device['hostname']} ({device['ip_address']})")
                return connection
                
        except NetmikoTimeoutException:
            logger.error(f"Timeout connecting to {device['hostname']} ({device['ip_address']})")
        except NetmikoAuthenticationException:
            logger.error(f"Authentication failed for {device['hostname']} ({device['ip_address']})")
        except Exception as e:
            logger.error(f"Error connecting to {device['hostname']}: {e}")
        
        return None
    
    def disconnect_device(self, device_id: str):
        """Disconnect from device"""
        with self.connection_lock:
            if device_id in self.connections:
                try:
                    self.connections[device_id].disconnect()
                except:
                    pass
                del self.connections[device_id]
                logger.info(f"Disconnected from device: {device_id}")
    
    def execute_command(self, device_id: str, command: str) -> Optional[str]:
        """
        Execute command on device
        
        Args:
            device_id: Device ID
            command: Command to execute
            
        Returns:
            str: Command output or None
        """
        connection = self.connect_to_device(device_id)
        if not connection:
            return None
        
        try:
            output = connection.send_command(command)
            logger.info(f"Executed command '{command}' on device {device_id}")
            return output
        except Exception as e:
            logger.error(f"Error executing command '{command}' on device {device_id}: {e}")
            return None
    
    def discover_device_info(self, device_id: str) -> Dict:
        """
        Discover and update device information
        
        Args:
            device_id: Device ID
            
        Returns:
            Dict: Discovered device information
        """
        connection = self.connect_to_device(device_id)
        if not connection:
            return {}
        
        device_info = {}
        
        try:
            # Get device version information
            version_output = connection.send_command('show version')
            device_info['version_output'] = version_output
            
            # Parse vendor-specific information
            device = self.get_device(device_id)
            if 'cisco' in device['device_type'].lower():
                device_info.update(self._parse_cisco_version(version_output))
            
            # Get interface information
            interfaces_output = connection.send_command('show ip interface brief')
            device_info['interfaces'] = self._parse_interfaces(interfaces_output, device['device_type'])
            
            # Update database with discovered info
            updates = {}
            if 'model' in device_info:
                updates['model'] = device_info['model']
            if 'os_version' in device_info:
                updates['os_version'] = device_info['os_version']
            
            if updates:
                self.update_device(device_id, updates)
            
            logger.info(f"Discovered device info for {device_id}")
            
        except Exception as e:
            logger.error(f"Error discovering device info for {device_id}: {e}")
        
        return device_info
    
    def _parse_cisco_version(self, version_output: str) -> Dict:
        """Parse Cisco version output"""
        info = {}
        lines = version_output.split('\n')
        
        for line in lines:
            line = line.strip()
            if 'Cisco IOS' in line:
                # Extract IOS version
                if 'Version' in line:
                    parts = line.split('Version')
                    if len(parts) > 1:
                        info['os_version'] = parts[1].split(',')[0].strip()
            elif line.startswith('cisco') and '(' in line:
                # Extract model
                model_part = line.split('(')[0].replace('cisco', '').strip()
                if model_part:
                    info['model'] = model_part
                    
        return info
    
    def _parse_interfaces(self, interfaces_output: str, device_type: str) -> List[Dict]:
        """Parse interface information"""
        interfaces = []
        lines = interfaces_output.split('\n')
        
        for line in lines[1:]:  # Skip header
            if line.strip() and not line.startswith('Interface'):
                parts = line.split()
                if len(parts) >= 2:
                    interface = {
                        'name': parts[0],
                        'ip_address': parts[1] if len(parts) > 1 else '',
                        'status': parts[4] if len(parts) > 4 else 'unknown',
                        'protocol': parts[5] if len(parts) > 5 else 'unknown'
                    }
                    interfaces.append(interface)
        
        return interfaces
    
    def bulk_execute_command(self, device_ids: List[str], command: str) -> Dict[str, str]:
        """
        Execute command on multiple devices concurrently
        
        Args:
            device_ids: List of device IDs
            command: Command to execute
            
        Returns:
            Dict: Device ID -> Command output mapping
        """
        results = {}
        
        def execute_on_device(device_id):
            output = self.execute_command(device_id, command)
            return device_id, output
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_device = {executor.submit(execute_on_device, device_id): device_id 
                              for device_id in device_ids}
            
            for future in as_completed(future_to_device):
                device_id, output = future.result()
                results[device_id] = output
        
        logger.info(f"Bulk command execution completed for {len(device_ids)} devices")
        return results
    
    def get_device_statistics(self) -> Dict:
        """Get device inventory statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT 
                    COUNT(*) as total_devices,
                    COUNT(CASE WHEN status = 'online' THEN 1 END) as online_devices,
                    COUNT(CASE WHEN status = 'offline' THEN 1 END) as offline_devices,
                    COUNT(DISTINCT vendor) as unique_vendors,
                    COUNT(DISTINCT device_type) as unique_device_types
                FROM devices
            ''')
            
            stats = dict(cursor.fetchone())
            
            # Get vendor distribution
            cursor = conn.execute('''
                SELECT vendor, COUNT(*) as count 
                FROM devices 
                WHERE vendor != '' 
                GROUP BY vendor
            ''')
            
            stats['vendor_distribution'] = dict(cursor.fetchall())
            
            return stats
    
    def __del__(self):
        """Cleanup connections on object destruction"""
        with self.connection_lock:
            for device_id in list(self.connections.keys()):
                try:
                    self.connections[device_id].disconnect()
                except:
                    pass
            self.connections.clear()
