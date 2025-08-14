"""
Configuration Management Module

Features:
- View device configurations from Catalyst Center
- Create and manage configuration templates
- Compare configurations
- Backup and restore configurations
"""

import json
import logging
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ConfigTemplate:
    id: str
    name: str
    description: str
    device_type: str
    config_data: str
    created_at: datetime
    updated_at: datetime

class ConfigurationManager:
    """Configuration management system"""
    
    def __init__(self):
        self.db_path = "data/configurations.db"
        self._init_database()
    
    def _init_database(self):
        """Initialize configuration database"""
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # Configuration templates
            conn.execute('''
                CREATE TABLE IF NOT EXISTS config_templates (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    device_type TEXT NOT NULL,
                    config_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Configuration backups
            conn.execute('''
                CREATE TABLE IF NOT EXISTS config_backups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    device_name TEXT,
                    config_data TEXT NOT NULL,
                    backup_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def get_device_configuration(self, device_id: str) -> Dict:
        """Get current device configuration from Catalyst Center"""
        try:
            from modules.catalyst_center_integration import CatalystCenterManager
            catalyst_manager = CatalystCenterManager()
            
            # Get device details
            devices = catalyst_manager.get_device_inventory()
            device = next((d for d in devices if d['id'] == device_id), None)
            
            if not device:
                return {"error": "Device not found"}
            
            # Simulate getting configuration (Always-On is read-only)
            config_data = self._get_simulated_config(device)
            
            return {
                "device_id": device_id,
                "device_name": device['name'],
                "device_type": device.get('type', 'Unknown'),
                "config_data": config_data,
                "last_updated": datetime.now().isoformat(),
                "source": "catalyst_center_readonly"
            }
            
        except Exception as e:
            logger.error(f"Error getting device configuration: {e}")
            return {"error": str(e)}
    
    def _get_simulated_config(self, device: Dict) -> str:
        """Generate simulated configuration for demo purposes"""
        device_name = device['name']
        device_ip = device['host']
        
        return f"""!
! Configuration for {device_name}
!
version 16.12
service timestamps debug datetime msec
service timestamps log datetime msec
!
hostname {device_name}
!
enable secret cisco123
!
interface GigabitEthernet0/0/0
 description WAN Interface
 ip address {device_ip} 255.255.255.0
 no shutdown
!
interface GigabitEthernet0/0/1
 description LAN Interface
 ip address 192.168.1.1 255.255.255.0
 no shutdown
!
router ospf 1
 network 192.168.1.0 0.0.0.255 area 0
!
line con 0
 password cisco
 login
line vty 0 4
 password cisco
 login
!
end"""
    
    def create_template(self, template_data: Dict) -> bool:
        """Create a new configuration template"""
        try:
            template_id = f"tpl_{int(datetime.now().timestamp())}"
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO config_templates (
                        id, name, description, device_type, config_data
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    template_id,
                    template_data['name'],
                    template_data.get('description', ''),
                    template_data['device_type'],
                    template_data['config_data']
                ))
                conn.commit()
            
            logger.info(f"Created configuration template: {template_data['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            return False
    
    def get_templates(self) -> List[Dict]:
        """Get all configuration templates"""
        templates = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT * FROM config_templates 
                    ORDER BY updated_at DESC
                ''')
                
                for row in cursor.fetchall():
                    templates.append(dict(row))
        
        except Exception as e:
            logger.error(f"Error getting templates: {e}")
        
        return templates
    
    def backup_device_config(self, device_id: str, config_data: str, device_name: str = None) -> bool:
        """Backup device configuration"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO config_backups (
                        device_id, device_name, config_data
                    ) VALUES (?, ?, ?)
                ''', (device_id, device_name, config_data))
                conn.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error backing up configuration: {e}")
            return False
    
    def get_config_backups(self, device_id: str = None, limit: int = 10) -> List[Dict]:
        """Get configuration backups"""
        backups = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                if device_id:
                    cursor = conn.execute('''
                        SELECT * FROM config_backups 
                        WHERE device_id = ?
                        ORDER BY backup_timestamp DESC
                        LIMIT ?
                    ''', (device_id, limit))
                else:
                    cursor = conn.execute('''
                        SELECT * FROM config_backups 
                        ORDER BY backup_timestamp DESC
                        LIMIT ?
                    ''', (limit,))
                
                for row in cursor.fetchall():
                    backups.append(dict(row))
        
        except Exception as e:
            logger.error(f"Error getting backups: {e}")
        
        return backups
    
    def compare_configurations(self, config1: str, config2: str) -> Dict:
        """Compare two configurations and return differences"""
        try:
            import difflib
            
            config1_lines = config1.splitlines()
            config2_lines = config2.splitlines()
            
            differ = difflib.unified_diff(
                config1_lines, 
                config2_lines, 
                fromfile='Current Config',
                tofile='Template Config',
                lineterm=''
            )
            
            diff_lines = list(differ)
            
            return {
                "has_differences": len(diff_lines) > 0,
                "diff_lines": diff_lines,
                "added_lines": [line[1:] for line in diff_lines if line.startswith('+') and not line.startswith('+++')],
                "removed_lines": [line[1:] for line in diff_lines if line.startswith('-') and not line.startswith('---')],
                "total_changes": len([line for line in diff_lines if line.startswith(('+', '-')) and not line.startswith(('+++', '---'))])
            }
            
        except Exception as e:
            logger.error(f"Error comparing configurations: {e}")
            return {"error": str(e)}
    
    def get_template_by_id(self, template_id: str) -> Optional[Dict]:
        """Get specific template by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    'SELECT * FROM config_templates WHERE id = ?', 
                    (template_id,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
                
        except Exception as e:
            logger.error(f"Error getting template: {e}")
            return None
    
    def delete_template(self, template_id: str) -> bool:
        """Delete a configuration template"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    'DELETE FROM config_templates WHERE id = ?',
                    (template_id,)
                )
                conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting template: {e}")
            return False