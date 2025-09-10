#!/usr/bin/env python3
"""
Ansible Manager Module

Provides Ansible automation capabilities for network device management.
Enables Infrastructure as Code (IaC) for network automation tasks.

Author: Network Automation Dashboard
Features: Playbook execution, inventory generation, job management
"""

import ansible_runner
import yaml
import json
import os
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import subprocess

logger = logging.getLogger(__name__)

class AnsibleManager:
    """
    Manages Ansible playbook execution and automation tasks
    
    Features:
    - Dynamic inventory generation from device database
    - Playbook execution with real-time monitoring
    - Job status tracking and history
    - Template-based configuration management
    """
    
    def __init__(self, playbook_dir: str = "ansible_playbooks"):
        """Initialize Ansible Manager"""
        self.playbook_dir = Path(playbook_dir)
        self.inventory_dir = self.playbook_dir / "inventory"
        self.roles_dir = self.playbook_dir / "roles"
        self.group_vars_dir = self.playbook_dir / "group_vars"
        
        # Ensure directories exist
        self._ensure_directories()
        
        # Job tracking
        self.active_jobs = {}
        
        logger.info("🎭 Ansible Manager initialized")
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        for directory in [self.playbook_dir, self.inventory_dir, self.roles_dir, self.group_vars_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def generate_inventory(self, devices: List[Dict]) -> Dict[str, Any]:
        """
        Generate Ansible inventory from device list
        
        Args:
            devices: List of device dictionaries from device manager
            
        Returns:
            Ansible inventory dictionary
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
        """
        Save inventory to YAML file
        
        Args:
            inventory: Inventory dictionary
            filename: Output filename
            
        Returns:
            Path to saved inventory file
        """
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
        Execute Ansible playbook
        
        Args:
            playbook_name: Name of playbook to execute
            inventory: Ansible inventory
            extra_vars: Additional variables for playbook
            limit: Limit execution to specific hosts
            
        Returns:
            Execution result dictionary
        """
        try:
            job_id = str(uuid.uuid4())
            playbook_path = self.playbook_dir / playbook_name
            
            # Check if playbook exists
            if not playbook_path.exists():
                raise FileNotFoundError(f"Playbook {playbook_name} not found")
            
            # Save inventory to temporary file
            inventory_file = self.save_inventory_file(inventory, f"temp_inventory_{job_id}.yml")
            
            # Prepare extra variables
            if extra_vars is None:
                extra_vars = {}
            
            # Add job tracking
            job_start = datetime.now()
            
            logger.info(f"🚀 Starting playbook execution: {playbook_name} (Job ID: {job_id})")
            
            # Execute playbook
            result = ansible_runner.run(
                playbook=str(playbook_path),
                inventory=inventory_file,
                extravars=extra_vars,
                limit=limit,
                quiet=False,
                verbosity=2
            )
            
            job_end = datetime.now()
            duration = (job_end - job_start).total_seconds()
            
            # Process results
            execution_result = {
                'job_id': job_id,
                'status': 'success' if result.status == 'successful' else 'failed',
                'playbook': playbook_name,
                'start_time': job_start.isoformat(),
                'end_time': job_end.isoformat(),
                'duration': duration,
                'return_code': result.rc,
                'stdout': result.stdout.read() if result.stdout else '',
                'stderr': result.stderr.read() if result.stderr else '',
                'stats': result.stats if hasattr(result, 'stats') else {},
                'events': []
            }
            
            # Collect events
            if hasattr(result, 'events'):
                for event in result.events:
                    execution_result['events'].append({
                        'event': event.get('event', ''),
                        'stdout': event.get('stdout', ''),
                        'host': event.get('event_data', {}).get('host', ''),
                        'task': event.get('event_data', {}).get('task', '')
                    })
            
            # Cleanup temporary inventory
            try:
                os.remove(inventory_file)
            except:
                pass
            
            logger.info(f"✅ Playbook execution completed: {execution_result['status']} ({duration:.2f}s)")
            return execution_result
            
        except Exception as e:
            logger.error(f"❌ Playbook execution failed: {e}")
            return {
                'job_id': job_id if 'job_id' in locals() else 'unknown',
                'status': 'failed',
                'error': str(e),
                'start_time': datetime.now().isoformat()
            }
    
    def get_available_playbooks(self) -> List[Dict[str, str]]:
        """
        Get list of available playbooks
        
        Returns:
            List of playbook information dictionaries
        """
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
    
    def validate_playbook(self, playbook_path: str) -> Tuple[bool, str]:
        """
        Validate Ansible playbook syntax
        
        Args:
            playbook_path: Path to playbook file
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            result = subprocess.run([
                'ansible-playbook', 
                '--syntax-check', 
                playbook_path
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return True, "Playbook syntax is valid"
            else:
                return False, result.stderr or result.stdout
                
        except subprocess.TimeoutExpired:
            return False, "Validation timeout"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
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
        
        # Save playbooks
        playbooks = {
            'backup_devices.yml': backup_playbook,
            'test_connectivity.yml': connectivity_playbook
        }
        
        for filename, content in playbooks.items():
            playbook_path = self.playbook_dir / filename
            with open(playbook_path, 'w') as f:
                yaml.dump(content, f, default_flow_style=False, indent=2)
            logger.info(f"📝 Created playbook: {filename}")
    
    def get_job_history(self, limit: int = 50) -> List[Dict]:
        """
        Get job execution history
        
        Args:
            limit: Maximum number of jobs to return
            
        Returns:
            List of job execution records
        """
        # This would typically fetch from database
        # For now, return empty list as placeholder
        return []
    
    def cleanup_old_jobs(self, days: int = 7):
        """Clean up old job artifacts and logs"""
        try:
            # Clean up temporary inventory files
            for temp_file in self.inventory_dir.glob("temp_inventory_*.yml"):
                if temp_file.stat().st_mtime < (datetime.now().timestamp() - (days * 24 * 3600)):
                    temp_file.unlink()
                    logger.info(f"🗑️ Cleaned up old inventory file: {temp_file.name}")
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")


# Example usage and testing
if __name__ == "__main__":
    # Initialize manager
    manager = AnsibleManager()
    
    # Create basic playbooks
    manager.create_basic_playbooks()
    
    # Test inventory generation
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
    print("Generated Inventory:")
    print(yaml.dump(inventory, default_flow_style=False, indent=2))
    
    # List available playbooks
    playbooks = manager.get_available_playbooks()
    print(f"\nAvailable Playbooks: {len(playbooks)}")
    for pb in playbooks:
        print(f"- {pb['name']}: {pb['description']}")
