#!/usr/bin/env python3
"""
Configuration Manager Module

Handles device configuration backup, restore, templating, and compliance checking.
Demonstrates configuration management best practices and automation.
"""

import json
import logging
import os
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import yaml
import jinja2
from pathlib import Path
import difflib
import hashlib

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Network device configuration management system
    
    Features:
    - Configuration backup and restore
    - Template-based configuration deployment
    - Configuration compliance checking
    - Change tracking and rollback
    - Multi-vendor support
    """
    
    def __init__(self, config_file: str = "config.json"):
        self.config = self._load_config(config_file)
        self.db_path = "data/configurations.db"
        self.backup_dir = Path("backups")
        self.templates_dir = Path("config/templates")
        
        # Create directories
        self.backup_dir.mkdir(exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        self._init_database()
        self._create_default_templates()
        
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get('backup', {})
        except FileNotFoundError:
            logger.warning(f"Config file {config_file} not found, using defaults")
            return {"retention_days": 30, "compression": True}
    
    def _init_database(self):
        """Initialize configuration database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # Configuration backups
            conn.execute('''
                CREATE TABLE IF NOT EXISTS config_backups (
                    id TEXT PRIMARY KEY,
                    device_id TEXT NOT NULL,
                    backup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    config_hash TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    size_bytes INTEGER,
                    backup_type TEXT DEFAULT 'automatic',
                    description TEXT,
                    created_by TEXT DEFAULT 'system'
                )
            ''')
            
            # Configuration templates
            conn.execute('''
                CREATE TABLE IF NOT EXISTS config_templates (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    vendor TEXT,
                    device_type TEXT,
                    template_content TEXT NOT NULL,
                    variables TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT DEFAULT 'system'
                )
            ''')
            
            # Configuration deployments
            conn.execute('''
                CREATE TABLE IF NOT EXISTS config_deployments (
                    id TEXT PRIMARY KEY,
                    device_id TEXT NOT NULL,
                    template_id TEXT,
                    deployment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT NOT NULL,
                    config_content TEXT,
                    variables_used TEXT,
                    error_message TEXT,
                    deployed_by TEXT DEFAULT 'system'
                )
            ''')
            
            # Compliance checks
            conn.execute('''
                CREATE TABLE IF NOT EXISTS compliance_checks (
                    id TEXT PRIMARY KEY,
                    device_id TEXT NOT NULL,
                    check_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    rule_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details TEXT,
                    severity TEXT DEFAULT 'medium'
                )
            ''')
            
            conn.commit()
            logger.info("Configuration database initialized")
    
    def backup_device_config(self, device_id: str, backup_type: str = "automatic", description: str = "") -> str:
        """
        Backup device configuration
        
        Args:
            device_id: Device ID
            backup_type: Type of backup (automatic, manual, scheduled)
            description: Optional description
            
        Returns:
            str: Backup ID
        """
        from .device_manager import DeviceManager
        
        device_manager = DeviceManager()
        device = device_manager.get_device(device_id)
        
        if not device:
            raise ValueError(f"Device not found: {device_id}")
        
        try:
            # Get device configuration
            connection = device_manager.connect_to_device(device_id)
            if not connection:
                raise Exception("Failed to connect to device")
            
            # Get running configuration
            config_content = self._get_device_config_content(connection, device['device_type'])
            
            if not config_content:
                raise Exception("Failed to retrieve configuration")
            
            # Generate backup ID and file path
            backup_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{device['hostname']}_{timestamp}_{backup_id[:8]}.cfg"
            file_path = self.backup_dir / filename
            
            # Calculate configuration hash
            config_hash = hashlib.sha256(config_content.encode()).hexdigest()
            
            # Save configuration to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            # Store backup information in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO config_backups (
                        id, device_id, config_hash, file_path, size_bytes,
                        backup_type, description
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    backup_id,
                    device_id,
                    config_hash,
                    str(file_path),
                    len(config_content.encode()),
                    backup_type,
                    description
                ))
                conn.commit()
            
            logger.info(f"Configuration backed up for device {device_id}: {filename}")
            return backup_id
            
        except Exception as e:
            logger.error(f"Error backing up configuration for device {device_id}: {e}")
            raise
    
    def _get_device_config_content(self, connection, device_type: str) -> str:
        """Get configuration content based on device type"""
        config_commands = {
            'cisco_ios': 'show running-config',
            'cisco_nxos': 'show running-config',
            'cisco_asa': 'show running-config',
            'juniper_junos': 'show configuration',
            'arista_eos': 'show running-config',
            'hp_procurve': 'show running-config'
        }
        
        command = config_commands.get(device_type, 'show running-config')
        
        try:
            config_content = connection.send_command(command, delay_factor=2)
            return config_content
        except Exception as e:
            logger.error(f"Error getting config content: {e}")
            return ""
    
    def get_device_config(self, device_id: str) -> Optional[str]:
        """Get current device configuration"""
        from .device_manager import DeviceManager
        
        device_manager = DeviceManager()
        connection = device_manager.connect_to_device(device_id)
        
        if not connection:
            return None
        
        device = device_manager.get_device(device_id)
        return self._get_device_config_content(connection, device['device_type'])
    
    def restore_device_config(self, device_id: str, backup_id: str) -> bool:
        """
        Restore device configuration from backup
        
        Args:
            device_id: Device ID
            backup_id: Backup ID to restore
            
        Returns:
            bool: Success status
        """
        try:
            # Get backup information
            backup = self.get_backup_info(backup_id)
            if not backup or backup['device_id'] != device_id:
                raise ValueError("Backup not found or device mismatch")
            
            # Read configuration from backup file
            with open(backup['file_path'], 'r', encoding='utf-8') as f:
                config_content = f.read()
            
            # Deploy configuration to device
            success = self._deploy_config_to_device(device_id, config_content)
            
            if success:
                logger.info(f"Configuration restored for device {device_id} from backup {backup_id}")
            else:
                logger.error(f"Failed to restore configuration for device {device_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error restoring configuration: {e}")
            return False
    
    def _deploy_config_to_device(self, device_id: str, config_content: str) -> bool:
        """Deploy configuration content to device"""
        from .device_manager import DeviceManager
        
        device_manager = DeviceManager()
        device = device_manager.get_device(device_id)
        connection = device_manager.connect_to_device(device_id)
        
        if not connection or not device:
            return False
        
        try:
            device_type = device['device_type'].lower()
            
            if 'cisco' in device_type:
                return self._deploy_cisco_config(connection, config_content)
            elif 'juniper' in device_type:
                return self._deploy_juniper_config(connection, config_content)
            elif 'arista' in device_type:
                return self._deploy_arista_config(connection, config_content)
            else:
                logger.warning(f"Configuration deployment not supported for device type: {device_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error deploying configuration: {e}")
            return False
    
    def _deploy_cisco_config(self, connection, config_content: str) -> bool:
        """Deploy configuration to Cisco device"""
        try:
            # Enter configuration mode
            connection.send_command("configure terminal")
            
            # Split configuration into commands
            config_lines = config_content.split('\n')
            
            for line in config_lines:
                line = line.strip()
                if line and not line.startswith('!') and not line.startswith('Building'):
                    connection.send_command(line, expect_string=r'#')
            
            # Save configuration
            connection.send_command("end")
            connection.send_command("write memory")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deploying Cisco configuration: {e}")
            return False
    
    def _deploy_juniper_config(self, connection, config_content: str) -> bool:
        """Deploy configuration to Juniper device"""
        try:
            # This is a simplified implementation
            # In production, you'd use NETCONF or proper Junos configuration methods
            connection.send_command("configure")
            connection.send_command("load replace terminal")
            
            # Send configuration content
            connection.send_command(config_content)
            connection.send_command("^D")  # End of input
            
            # Commit configuration
            connection.send_command("commit")
            connection.send_command("exit")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deploying Juniper configuration: {e}")
            return False
    
    def _deploy_arista_config(self, connection, config_content: str) -> bool:
        """Deploy configuration to Arista device"""
        try:
            # Similar to Cisco implementation
            connection.send_command("configure")
            
            config_lines = config_content.split('\n')
            for line in config_lines:
                line = line.strip()
                if line and not line.startswith('!'):
                    connection.send_command(line)
            
            connection.send_command("end")
            connection.send_command("write memory")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deploying Arista configuration: {e}")
            return False
    
    def get_backup_info(self, backup_id: str) -> Optional[Dict]:
        """Get backup information"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT * FROM config_backups WHERE id = ?', (backup_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def get_device_backups(self, device_id: str, limit: int = 20) -> List[Dict]:
        """Get backup history for device"""
        backups = []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM config_backups 
                WHERE device_id = ? 
                ORDER BY backup_date DESC 
                LIMIT ?
            ''', (device_id, limit))
            
            for row in cursor.fetchall():
                backups.append(dict(row))
        
        return backups
    
    def create_config_template(self, name: str, description: str, vendor: str, 
                             device_type: str, template_content: str, 
                             variables: List[str] = None) -> str:
        """
        Create configuration template
        
        Args:
            name: Template name
            description: Template description
            vendor: Device vendor
            device_type: Device type
            template_content: Jinja2 template content
            variables: List of template variables
            
        Returns:
            str: Template ID
        """
        template_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO config_templates (
                    id, name, description, vendor, device_type,
                    template_content, variables
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                template_id,
                name,
                description,
                vendor,
                device_type,
                template_content,
                json.dumps(variables or [])
            ))
            conn.commit()
        
        # Save template to file
        template_file = self.templates_dir / f"{name}.j2"
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        logger.info(f"Created configuration template: {name}")
        return template_id
    
    def get_config_templates(self) -> List[Dict]:
        """Get all configuration templates"""
        templates = []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT * FROM config_templates ORDER BY name')
            
            for row in cursor.fetchall():
                template = dict(row)
                template['variables'] = json.loads(template['variables'] or '[]')
                templates.append(template)
        
        return templates
    
    def deploy_template(self, device_id: str, template_id: str, variables: Dict = None) -> str:
        """
        Deploy configuration template to device
        
        Args:
            device_id: Device ID
            template_id: Template ID
            variables: Template variables
            
        Returns:
            str: Deployment ID
        """
        deployment_id = str(uuid.uuid4())
        
        try:
            # Get template
            template = self.get_template(template_id)
            if not template:
                raise ValueError("Template not found")
            
            # Render template with variables
            jinja_template = self.jinja_env.from_string(template['template_content'])
            config_content = jinja_template.render(variables or {})
            
            # Deploy to device
            success = self._deploy_config_to_device(device_id, config_content)
            
            # Record deployment
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO config_deployments (
                        id, device_id, template_id, status, config_content, variables_used
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    deployment_id,
                    device_id,
                    template_id,
                    'success' if success else 'failed',
                    config_content,
                    json.dumps(variables or {})
                ))
                conn.commit()
            
            logger.info(f"Template deployed to device {device_id}: {template['name']}")
            return deployment_id
            
        except Exception as e:
            logger.error(f"Error deploying template: {e}")
            # Record failed deployment
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO config_deployments (
                        id, device_id, template_id, status, error_message
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (deployment_id, device_id, template_id, 'failed', str(e)))
                conn.commit()
            
            raise
    
    def get_template(self, template_id: str) -> Optional[Dict]:
        """Get template by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT * FROM config_templates WHERE id = ?', (template_id,))
            row = cursor.fetchone()
            
            if row:
                template = dict(row)
                template['variables'] = json.loads(template['variables'] or '[]')
                return template
            return None
    
    def compare_configs(self, config1: str, config2: str) -> Dict:
        """
        Compare two configurations and return differences
        
        Args:
            config1: First configuration
            config2: Second configuration
            
        Returns:
            Dict: Comparison results
        """
        lines1 = config1.splitlines(keepends=True)
        lines2 = config2.splitlines(keepends=True)
        
        diff = list(difflib.unified_diff(lines1, lines2, 
                                       fromfile='config1', 
                                       tofile='config2',
                                       lineterm=''))
        
        return {
            'has_differences': len(diff) > 0,
            'diff_lines': diff,
            'diff_html': difflib.HtmlDiff().make_file(lines1, lines2, 
                                                    'Configuration 1', 
                                                    'Configuration 2')
        }
    
    def check_compliance(self, device_id: str, rules: List[Dict] = None) -> List[Dict]:
        """
        Check device configuration compliance
        
        Args:
            device_id: Device ID
            rules: List of compliance rules
            
        Returns:
            List[Dict]: Compliance check results
        """
        if not rules:
            rules = self._get_default_compliance_rules()
        
        config_content = self.get_device_config(device_id)
        if not config_content:
            return []
        
        results = []
        
        for rule in rules:
            check_id = str(uuid.uuid4())
            status = self._check_compliance_rule(config_content, rule)
            
            result = {
                'check_id': check_id,
                'rule_name': rule['name'],
                'status': 'passed' if status['compliant'] else 'failed',
                'details': status['details'],
                'severity': rule.get('severity', 'medium')
            }
            
            results.append(result)
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO compliance_checks (
                        id, device_id, rule_name, status, details, severity
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    check_id,
                    device_id,
                    rule['name'],
                    result['status'],
                    result['details'],
                    result['severity']
                ))
                conn.commit()
        
        return results
    
    def _get_default_compliance_rules(self) -> List[Dict]:
        """Get default compliance rules"""
        return [
            {
                'name': 'SSH Version 2 Only',
                'description': 'Ensure only SSH version 2 is enabled',
                'pattern': r'ip ssh version 2',
                'type': 'required_line',
                'severity': 'high'
            },
            {
                'name': 'No Telnet Access',
                'description': 'Ensure telnet is disabled',
                'pattern': r'transport input ssh',
                'type': 'required_line',
                'severity': 'critical'
            },
            {
                'name': 'Enable Secret Configured',
                'description': 'Ensure enable secret is configured',
                'pattern': r'enable secret',
                'type': 'required_line',
                'severity': 'high'
            },
            {
                'name': 'No Default Passwords',
                'description': 'Ensure no default passwords are used',
                'pattern': r'username.*password.*cisco',
                'type': 'forbidden_line',
                'severity': 'critical'
            },
            {
                'name': 'Banner Configured',
                'description': 'Ensure login banner is configured',
                'pattern': r'banner (login|motd)',
                'type': 'required_line',
                'severity': 'medium'
            }
        ]
    
    def _check_compliance_rule(self, config_content: str, rule: Dict) -> Dict:
        """Check individual compliance rule"""
        import re
        
        pattern = rule['pattern']
        rule_type = rule['type']
        
        if rule_type == 'required_line':
            # Check if required pattern exists
            if re.search(pattern, config_content, re.MULTILINE | re.IGNORECASE):
                return {'compliant': True, 'details': 'Required configuration found'}
            else:
                return {'compliant': False, 'details': 'Required configuration missing'}
        
        elif rule_type == 'forbidden_line':
            # Check if forbidden pattern exists
            if re.search(pattern, config_content, re.MULTILINE | re.IGNORECASE):
                return {'compliant': False, 'details': 'Forbidden configuration found'}
            else:
                return {'compliant': True, 'details': 'No forbidden configuration detected'}
        
        elif rule_type == 'custom':
            # Custom validation logic would go here
            return {'compliant': True, 'details': 'Custom check passed'}
        
        return {'compliant': False, 'details': 'Unknown rule type'}
    
    def _create_default_templates(self):
        """Create default configuration templates"""
        default_templates = [
            {
                'name': 'Basic Router Configuration',
                'description': 'Basic router configuration template',
                'vendor': 'cisco',
                'device_type': 'router',
                'content': '''
! Basic Router Configuration
hostname {{ hostname }}
!
enable secret {{ enable_secret }}
!
interface {{ wan_interface }}
 ip address {{ wan_ip }} {{ wan_mask }}
 no shutdown
!
interface {{ lan_interface }}
 ip address {{ lan_ip }} {{ lan_mask }}
 no shutdown
!
ip route 0.0.0.0 0.0.0.0 {{ default_gateway }}
!
line vty 0 4
 transport input ssh
 login local
!
ip ssh version 2
!
banner motd ^
{{ banner_message }}
^
!
end
''',
                'variables': ['hostname', 'enable_secret', 'wan_interface', 'wan_ip', 'wan_mask', 
                            'lan_interface', 'lan_ip', 'lan_mask', 'default_gateway', 'banner_message']
            },
            {
                'name': 'Basic Switch Configuration',
                'description': 'Basic switch configuration template',
                'vendor': 'cisco',
                'device_type': 'switch',
                'content': '''
! Basic Switch Configuration
hostname {{ hostname }}
!
enable secret {{ enable_secret }}
!
vlan {{ management_vlan }}
 name Management
!
interface vlan{{ management_vlan }}
 ip address {{ management_ip }} {{ management_mask }}
 no shutdown
!
ip default-gateway {{ default_gateway }}
!
{% for port in access_ports %}
interface {{ port.interface }}
 switchport mode access
 switchport access vlan {{ port.vlan }}
 spanning-tree portfast
!
{% endfor %}
!
line vty 0 15
 transport input ssh
 login local
!
ip ssh version 2
!
banner motd ^
{{ banner_message }}
^
!
end
''',
                'variables': ['hostname', 'enable_secret', 'management_vlan', 'management_ip', 
                            'management_mask', 'default_gateway', 'access_ports', 'banner_message']
            }
        ]
        
        for template in default_templates:
            # Check if template already exists
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT id FROM config_templates WHERE name = ?', (template['name'],))
                if not cursor.fetchone():
                    self.create_config_template(
                        template['name'],
                        template['description'],
                        template['vendor'],
                        template['device_type'],
                        template['content'],
                        template['variables']
                    )
    
    def cleanup_old_backups(self):
        """Clean up old backup files"""
        retention_days = self.config.get('retention_days', 30)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get old backups
                cursor = conn.execute('''
                    SELECT id, file_path FROM config_backups 
                    WHERE backup_date < ?
                ''', (cutoff_date.isoformat(),))
                
                old_backups = cursor.fetchall()
                
                for backup_id, file_path in old_backups:
                    # Delete file
                    try:
                        os.remove(file_path)
                    except FileNotFoundError:
                        pass
                    
                    # Delete database record
                    conn.execute('DELETE FROM config_backups WHERE id = ?', (backup_id,))
                
                conn.commit()
                logger.info(f"Cleaned up {len(old_backups)} old backups")
                
        except Exception as e:
            logger.error(f"Error cleaning up old backups: {e}")
