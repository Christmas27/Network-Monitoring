#!/usr/bin/env python3
"""
Simplified Ansible Manager Module (Phase 1)

This is a simplified version to test the integration without full Ansible dependencies.
We'll add the full Ansible functionality once the package installation is resolved.
"""

import yaml
import json
import os
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class AnsibleManager:
    """
    Simplified Ansible Manager for testing integration
    
    This version provides the interface without requiring ansible-runner
    until we resolve the installation issue.
    """
    
    def __init__(self, playbook_dir: str = "ansible_playbooks"):
        """Initialize Ansible Manager"""
        self.playbook_dir = Path(playbook_dir)
        self.inventory_dir = self.playbook_dir / "inventory"
        self.roles_dir = self.playbook_dir / "roles"
        self.group_vars_dir = self.playbook_dir / "group_vars"
        
        # Ensure directories exist
        self._ensure_directories()
        
        logger.info("🎭 Ansible Manager initialized (Simplified Mode)")
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        for directory in [self.playbook_dir, self.inventory_dir, self.roles_dir, self.group_vars_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def generate_inventory(self, devices: List[Dict]) -> Dict[str, Any]:
        """
        Generate Ansible inventory from device list
        """
        try:
            inventory = {
                'all': {
                    'children': {
                        'routers': {'hosts': {}},
                        'switches': {'hosts': {}},
                        'firewalls': {'hosts': {}},
                        'unknown': {'hosts': {}}
                    },
                    'vars': {
                        'ansible_connection': 'network_cli',
                        'ansible_user': '{{ device_username }}',
                        'ansible_password': '{{ device_password }}',
                        'ansible_become': 'yes',
                        'ansible_become_method': 'enable'
                    }
                }
            }
            
            # Group devices by type
            for device in devices:
                device_name = device.get('hostname', device.get('name', 'unknown'))
                device_type = device.get('device_type', device.get('type', 'unknown')).lower()
                
                # Determine device group
                if 'router' in device_type:
                    group = 'routers'
                elif 'switch' in device_type:
                    group = 'switches'
                elif 'firewall' in device_type or 'asa' in device_type:
                    group = 'firewalls'
                else:
                    group = 'unknown'
                
                # Add device to inventory
                inventory['all']['children'][group]['hosts'][device_name] = {
                    'ansible_host': device.get('ip_address', device.get('host', device.get('ip'))),
                    'device_type': device_type,
                    'device_id': device.get('id'),
                    'ansible_network_os': self._map_device_os(device_type),
                    'device_vendor': device.get('vendor', 'cisco'),
                    'device_model': device.get('model', 'unknown'),
                    'device_role': device.get('role', 'access')
                }
            
            logger.info(f"📋 Generated inventory for {len(devices)} devices")
            return inventory
            
        except Exception as e:
            logger.error(f"❌ Error generating inventory: {e}")
            raise
    
    def _map_device_os(self, device_type: str) -> str:
        """Map device type to Ansible network OS"""
        os_mapping = {
            'cisco_ios': 'ios',
            'cisco_xe': 'ios',
            'cisco_xr': 'iosxr',
            'cisco_nxos': 'nxos',
            'cisco_asa': 'asa',
            'juniper': 'junos',
            'arista': 'eos',
            'hp': 'comware',
            'dell': 'dellos10'
        }
        
        for key, value in os_mapping.items():
            if key in device_type.lower():
                return value
        
        return 'ios'  # Default to IOS
    
    def save_inventory_file(self, inventory: Dict, filename: str = "dynamic_inventory.yml") -> str:
        """Save inventory to YAML file"""
        try:
            inventory_path = self.inventory_dir / filename
            
            with open(inventory_path, 'w') as f:
                yaml.dump(inventory, f, default_flow_style=False, indent=2)
            
            logger.info(f"💾 Inventory saved to {inventory_path}")
            return str(inventory_path)
            
        except Exception as e:
            logger.error(f"❌ Error saving inventory: {e}")
            raise
    
    def run_playbook(self, 
                    playbook_name: str, 
                    inventory: Dict, 
                    extra_vars: Optional[Dict] = None,
                    limit: Optional[str] = None) -> Dict[str, Any]:
        """
        Simulate playbook execution (simplified mode)
        """
        job_id = str(uuid.uuid4())
        
        # Simulate execution
        result = {
            'job_id': job_id,
            'status': 'simulated',  # In real mode this would be 'success' or 'failed'
            'playbook': playbook_name,
            'start_time': datetime.now().isoformat(),
            'end_time': datetime.now().isoformat(),
            'duration': 0.5,  # Simulated duration
            'message': 'Playbook execution simulated - Ansible not fully configured yet',
            'devices_targeted': len(inventory.get('all', {}).get('children', {}).get('routers', {}).get('hosts', {})) + 
                              len(inventory.get('all', {}).get('children', {}).get('switches', {}).get('hosts', {}))
        }
        
        logger.info(f"🎭 Simulated playbook execution: {playbook_name}")
        return result
    
    def get_available_playbooks(self) -> List[Dict[str, str]]:
        """Get list of available playbooks"""
        try:
            playbooks = []
            
            for playbook_file in self.playbook_dir.glob("*.yml"):
                if playbook_file.name.startswith('temp_'):
                    continue
                
                playbook_info = {
                    'name': playbook_file.name,
                    'path': str(playbook_file),
                    'size': playbook_file.stat().st_size,
                    'modified': datetime.fromtimestamp(playbook_file.stat().st_mtime).isoformat()
                }
                
                # Try to extract description from playbook
                try:
                    with open(playbook_file, 'r') as f:
                        content = yaml.safe_load(f)
                        if isinstance(content, list) and len(content) > 0:
                            playbook_info['description'] = content[0].get('name', 'No description')
                        else:
                            playbook_info['description'] = 'No description available'
                except:
                    playbook_info['description'] = 'Error reading playbook'
                
                playbooks.append(playbook_info)
            
            logger.info(f"📚 Found {len(playbooks)} available playbooks")
            return playbooks
            
        except Exception as e:
            logger.error(f"❌ Error listing playbooks: {e}")
            return []
    
    def create_basic_playbooks(self):
        """Create basic playbooks for common network tasks"""
        
        # Device backup playbook
        backup_playbook = [
            {
                'name': 'Network Device Configuration Backup',
                'hosts': 'all',
                'gather_facts': False,
                'tasks': [
                    {
                        'name': 'Backup device configuration',
                        'ios_config': {
                            'backup': True,
                            'backup_options': {
                                'filename': '{{ inventory_hostname }}_{{ ansible_date_time.date }}.cfg',
                                'dir_path': './backups/'
                            }
                        },
                        'when': "ansible_network_os == 'ios'"
                    },
                    {
                        'name': 'Display backup status',
                        'debug': {
                            'msg': 'Configuration backed up for {{ inventory_hostname }}'
                        }
                    }
                ]
            }
        ]
        
        # Connectivity test playbook
        connectivity_playbook = [
            {
                'name': 'Network Device Connectivity Test',
                'hosts': 'all',
                'gather_facts': False,
                'tasks': [
                    {
                        'name': 'Test device connectivity',
                        'wait_for_connection': {
                            'timeout': 30
                        }
                    },
                    {
                        'name': 'Gather device facts',
                        'ios_facts': {
                            'gather_subset': ['all']
                        },
                        'when': "ansible_network_os == 'ios'"
                    },
                    {
                        'name': 'Display device information',
                        'debug': {
                            'msg': 'Successfully connected to {{ inventory_hostname }} - {{ ansible_net_version | default("Unknown version") }}'
                        }
                    }
                ]
            }
        ]
        
        # Configuration management playbook
        config_mgmt_playbook = [
            {
                'name': 'Network Device Configuration Management',
                'hosts': 'all',
                'gather_facts': False,
                'vars': {
                    'config_commands': [
                        'hostname {{ inventory_hostname }}',
                        'ip domain-name example.com',
                        'ntp server 8.8.8.8'
                    ]
                },
                'tasks': [
                    {
                        'name': 'Apply basic configuration',
                        'ios_config': {
                            'lines': '{{ config_commands }}'
                        },
                        'when': "ansible_network_os == 'ios'"
                    },
                    {
                        'name': 'Save configuration',
                        'ios_config': {
                            'save_when': 'always'
                        },
                        'when': "ansible_network_os == 'ios'"
                    }
                ]
            }
        ]
        
        # Save playbooks
        playbooks = {
            'backup_devices.yml': backup_playbook,
            'test_connectivity.yml': connectivity_playbook,
            'configure_devices.yml': config_mgmt_playbook
        }
        
        for filename, content in playbooks.items():
            playbook_path = self.playbook_dir / filename
            with open(playbook_path, 'w') as f:
                yaml.dump(content, f, default_flow_style=False, indent=2)
            logger.info(f"📝 Created playbook: {filename}")
    
    def get_automation_status(self) -> Dict[str, Any]:
        """Get automation system status"""
        return {
            'status': 'simplified_mode',
            'ansible_available': False,
            'playbooks_count': len(self.get_available_playbooks()),
            'message': 'Ansible integration in development mode'
        }


# Test the module
if __name__ == "__main__":
    manager = AnsibleManager()
    manager.create_basic_playbooks()
    
    # Test with sample devices
    sample_devices = [
        {
            'id': '1',
            'hostname': 'router1',
            'ip_address': '192.168.1.1',
            'device_type': 'cisco_ios',
            'vendor': 'cisco'
        },
        {
            'id': '2', 
            'hostname': 'switch1',
            'ip_address': '192.168.1.2',
            'device_type': 'cisco_ios',
            'vendor': 'cisco'
        }
    ]
    
    inventory = manager.generate_inventory(sample_devices)
    print("✅ Simplified Ansible Manager working!")
    print(f"📋 Generated inventory for {len(sample_devices)} devices")
    print(f"📚 Available playbooks: {len(manager.get_available_playbooks())}")
