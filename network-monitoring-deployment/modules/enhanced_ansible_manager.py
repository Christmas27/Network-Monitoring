#!/usr/bin/env python3
"""
Enhanced Ansible Manager with Real Execution Support

This version supports both simulation and real Ansible execution
"""

import yaml
import json
import os
import uuid
import logging
import subprocess
import tempfile
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class EnhancedAnsibleManager:
    """Enhanced Ansible Manager with real execution capability"""
    
    def __init__(self, playbook_dir: str = "ansible_playbooks"):
        """Initialize Enhanced Ansible Manager"""
        self.playbook_dir = Path(playbook_dir)
        self.inventory_dir = self.playbook_dir / "inventory"
        self.roles_dir = self.playbook_dir / "roles"
        self.group_vars_dir = self.playbook_dir / "group_vars"
        
        # Check if Ansible is available
        self.ansible_available = self._check_ansible_availability()
        
        # Ensure directories exist
        self._ensure_directories()
        
        mode = "Real Execution" if self.ansible_available else "Simulation"
        logger.info(f"🎭 Enhanced Ansible Manager initialized ({mode})")
    
    def _check_ansible_availability(self) -> bool:
        """Check if Ansible is available"""
        try:
            result = subprocess.run(['ansible', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        for directory in [self.playbook_dir, self.inventory_dir, self.roles_dir, self.group_vars_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def generate_inventory(self, devices: List[Dict]) -> Dict[str, Any]:
        """Generate Ansible inventory from device list"""
        try:
            inventory = {
                'all': {
                    'hosts': {},
                    'vars': {
                        'ansible_connection': 'ssh',
                        'ansible_ssh_common_args': '-o StrictHostKeyChecking=no',
                        'ansible_host_key_checking': False
                    }
                },
                '_meta': {
                    'hostvars': {}
                }
            }
            
            # Group devices by type
            groups = {}
            
            for device in devices:
                hostname = device.get('hostname', f"device_{device.get('id', 'unknown')}")
                
                # Handle localhost:port format
                ip_address = device.get('ip_address', 'unknown')
                if ':' in ip_address:
                    host, port = ip_address.split(':')
                    ansible_host = host
                    ansible_port = int(port)
                else:
                    ansible_host = ip_address
                    ansible_port = device.get('ansible_port', device.get('port', 22))
                
                # Add to inventory
                inventory['all']['hosts'][hostname] = None
                
                # Add host variables
                inventory['_meta']['hostvars'][hostname] = {
                    'ansible_host': ansible_host,
                    'ansible_port': ansible_port,
                    'ansible_user': device.get('username', 'admin'),
                    'ansible_password': device.get('password', 'admin'),
                    'device_type': device.get('device_type', 'unknown'),
                    'vendor': device.get('vendor', 'unknown'),
                    'device_role': device.get('role', 'unknown')
                }
                
                # Group by device type
                device_type = device.get('device_type', 'unknown')
                if device_type not in groups:
                    groups[device_type] = {'hosts': {}}
                groups[device_type]['hosts'][hostname] = None
                
                # Group by role
                role = device.get('role', 'unknown')
                role_group = f"{role}s"
                if role_group not in groups:
                    groups[role_group] = {'hosts': {}}
                groups[role_group]['hosts'][hostname] = None
            
            # Add groups to inventory
            inventory.update(groups)
            
            logger.info(f"📋 Generated inventory for {len(devices)} devices")
            return inventory
            
        except Exception as e:
            logger.error(f"❌ Error generating inventory: {e}")
            raise
    
    def save_inventory_file(self, inventory: Dict, filename: str = "lab_inventory.yml") -> str:
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
    
    def run_playbook_real(self, playbook_name: str, inventory_file: str, 
                         extra_vars: Optional[Dict] = None) -> Dict[str, Any]:
        """Run playbook using real Ansible"""
        job_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Build ansible-playbook command
            cmd = [
                'ansible-playbook',
                str(self.playbook_dir / playbook_name),
                '-i', inventory_file,
                '-v'  # Verbose output
            ]
            
            # Add extra variables if provided
            if extra_vars:
                extra_vars_json = json.dumps(extra_vars)
                cmd.extend(['--extra-vars', extra_vars_json])
            
            logger.info(f"🚀 Executing: {' '.join(cmd)}")
            
            # Execute playbook
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=str(self.playbook_dir.parent)
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Parse results
            if result.returncode == 0:
                status = 'success'
                message = 'Playbook executed successfully!'
            else:
                status = 'failed'
                message = f'Playbook failed with return code {result.returncode}'
            
            return {
                'job_id': job_id,
                'status': status,
                'playbook': playbook_name,
                'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                'duration': round(duration, 2),
                'message': message,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode,
                'execution_mode': 'real'
            }
            
        except subprocess.TimeoutExpired:
            return {
                'job_id': job_id,
                'status': 'timeout',
                'playbook': playbook_name,
                'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'duration': 300,
                'message': 'Playbook execution timed out',
                'execution_mode': 'real'
            }
        except Exception as e:
            return {
                'job_id': job_id,
                'status': 'error',
                'playbook': playbook_name,
                'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'duration': 0,
                'message': f'Error executing playbook: {str(e)}',
                'execution_mode': 'real'
            }
    
    def run_playbook_simulation(self, playbook_name: str, devices_count: int = 0) -> Dict[str, Any]:
        """Simulate playbook execution"""
        job_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        # Simulate processing time
        import time
        time.sleep(0.5)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return {
            'job_id': job_id,
            'status': 'simulated',
            'playbook': playbook_name,
            'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration': round(duration, 2),
            'message': f'Playbook simulated successfully for {devices_count} devices',
            'devices_targeted': devices_count,
            'execution_mode': 'simulation'
        }
    
    def run_playbook(self, playbook_name: str, inventory: Dict, 
                    extra_vars: Optional[Dict] = None, 
                    limit: Optional[str] = None) -> Dict[str, Any]:
        """Run playbook (real or simulated based on availability)"""
        
        if self.ansible_available:
            # Real execution
            try:
                # Save inventory to temporary file
                inventory_file = self.save_inventory_file(inventory, f"temp_{uuid.uuid4().hex[:8]}.yml")
                
                # Run real playbook
                result = self.run_playbook_real(playbook_name, inventory_file, extra_vars)
                
                # Clean up temporary inventory file
                try:
                    os.remove(inventory_file)
                except:
                    pass
                
                return result
                
            except Exception as e:
                logger.error(f"❌ Real execution failed, falling back to simulation: {e}")
                # Fall back to simulation
                devices_count = len(inventory.get('all', {}).get('hosts', {}))
                return self.run_playbook_simulation(playbook_name, devices_count)
        else:
            # Simulation mode
            devices_count = len(inventory.get('all', {}).get('hosts', {}))
            return self.run_playbook_simulation(playbook_name, devices_count)
    
    def get_available_playbooks(self) -> List[Dict[str, Any]]:
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
                
                # Enhanced descriptions for lab playbooks
                if playbook_file.name.startswith('lab_'):
                    if 'connectivity' in playbook_file.name:
                        playbook_info['description'] = '🔗 Test lab device connectivity and system info (Real SSH)'
                        playbook_info['category'] = 'Lab Testing'
                    elif 'configuration' in playbook_file.name:
                        playbook_info['description'] = '⚙️ Apply configuration to lab devices (Real SSH)'
                        playbook_info['category'] = 'Lab Configuration'
                    elif 'monitoring' in playbook_file.name:
                        playbook_info['description'] = '📊 Monitor lab device performance (Real SSH)'
                        playbook_info['category'] = 'Lab Monitoring'
                    else:
                        playbook_info['description'] = '🧪 Lab device management (Real SSH)'
                        playbook_info['category'] = 'Lab Management'
                else:
                    # Try to extract description from playbook
                    try:
                        with open(playbook_file, 'r') as f:
                            content = yaml.safe_load(f)
                            if isinstance(content, list) and len(content) > 0:
                                playbook_info['description'] = content[0].get('name', 'Legacy playbook')
                                playbook_info['category'] = 'Legacy'
                            else:
                                playbook_info['description'] = 'Legacy playbook'
                                playbook_info['category'] = 'Legacy'
                    except:
                        playbook_info['description'] = 'Error reading playbook'
                        playbook_info['category'] = 'Unknown'
                
                playbooks.append(playbook_info)
            
            # Sort by category and name
            playbooks.sort(key=lambda x: (x.get('category', 'Unknown'), x['name']))
            
            logger.info(f"📚 Found {len(playbooks)} available playbooks")
            return playbooks
            
        except Exception as e:
            logger.error(f"❌ Error listing playbooks: {e}")
            return []
    
    def get_execution_status(self) -> Dict[str, Any]:
        """Get current execution capabilities"""
        return {
            'ansible_available': self.ansible_available,
            'execution_mode': 'real' if self.ansible_available else 'simulation',
            'playbooks_count': len(self.get_available_playbooks()),
            'supported_features': [
                'SSH connectivity testing',
                'System information gathering',
                'Configuration management',
                'Performance monitoring',
                'Real command execution' if self.ansible_available else 'Simulation mode'
            ]
        }

# Create enhanced manager instance
def get_enhanced_manager():
    """Get enhanced Ansible manager instance"""
    return EnhancedAnsibleManager()

if __name__ == "__main__":
    # Test the enhanced manager
    manager = get_enhanced_manager()
    
    print("🎭 Enhanced Ansible Manager Test")
    print("=" * 40)
    
    status = manager.get_execution_status()
    print(f"📊 Ansible Available: {status['ansible_available']}")
    print(f"🎮 Execution Mode: {status['execution_mode']}")
    print(f"📚 Available playbooks: {status['playbooks_count']}")
    
    playbooks = manager.get_available_playbooks()
    print(f"\n📋 Playbooks:")
    for pb in playbooks:
        print(f"  • {pb['name']} - {pb['description']}")
