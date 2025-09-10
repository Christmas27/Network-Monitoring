#!/usr/bin/env python3
"""
WSL Ansible Bridge - Execute Ansible commands through WSL Ubuntu
Bridges Windows Python environment to WSL Linux environment for Ansible execution
"""

import subprocess
import json
import tempfile
import os
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class WSLAnsibleBridge:
    """Bridge to execute Ansible commands in WSL Ubuntu environment"""
    
    def __init__(self):
        self.wsl_distro = "Ubuntu"  # Default WSL distro
        self.ansible_path = "/usr/bin/ansible-playbook"
        self.inventory_path = "/tmp/lab_inventory.yml"
        
        # Try to detect the actual Ubuntu distro name
        try:
            result = subprocess.run(
                ["wsl", "--list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'ubuntu' in line.lower() and 'docker' not in line.lower():
                        # Extract distro name, removing special characters
                        distro_name = line.strip().replace('*', '').strip()
                        if distro_name and distro_name != '':
                            self.wsl_distro = distro_name
                            break
        except:
            pass  # Use default "Ubuntu"
        
    def check_wsl_availability(self) -> Dict[str, Any]:
        """Check if WSL and Ansible are available"""
        try:
            # Check WSL
            result = subprocess.run(
                ["wsl", "--list", "--verbose"],
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-16le'  # WSL outputs in UTF-16LE
            )
            
            if result.returncode != 0:
                return {
                    "status": "failed",
                    "error": "WSL not available",
                    "wsl_available": False,
                    "ansible_available": False
                }
            
            # Check if Ubuntu distro exists (be more flexible)
            output_lower = result.stdout.lower()
            # Look for "ubuntu" but not in a line that contains "docker"
            ubuntu_found = False
            for line in output_lower.split('\n'):
                if 'ubuntu' in line and 'docker' not in line:
                    ubuntu_found = True
                    break
            
            logger.info(f"🔍 WSL output lines: {output_lower.split(chr(10))}")
            logger.info(f"🔍 Ubuntu found: {ubuntu_found}")
            
            if not ubuntu_found:
                return {
                    "status": "failed",
                    "error": "Ubuntu distro not found in WSL",
                    "wsl_available": True,
                    "ansible_available": False
                }
            
            # Check Ansible in WSL
            ansible_check = subprocess.run(
                ["wsl", "-d", self.wsl_distro, "--", "which", "ansible-playbook"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            logger.info(f"🔍 Ansible check return code: {ansible_check.returncode}")
            logger.info(f"🔍 Ansible check stdout: '{ansible_check.stdout.strip()}'")
            logger.info(f"🔍 Ansible check stderr: '{ansible_check.stderr.strip()}'")
            
            ansible_available = ansible_check.returncode == 0 and ansible_check.stdout.strip()
            
            if ansible_available:
                # Get Ansible version
                version_result = subprocess.run(
                    ["wsl", "-d", self.wsl_distro, "--", "ansible-playbook", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if version_result.returncode == 0:
                    # Extract version from first line
                    version_line = version_result.stdout.split('\n')[0]
                    if '[' in version_line and ']' in version_line:
                        ansible_version = version_line.split('[')[1].split(']')[0]
                    else:
                        ansible_version = version_line.strip()
                else:
                    ansible_version = "Unknown"
            else:
                ansible_version = "Not installed"
            
            return {
                "status": "success",
                "wsl_available": True,
                "ansible_available": ansible_available,
                "ansible_version": ansible_version,
                "distro": self.wsl_distro
            }
            
        except subprocess.TimeoutExpired:
            return {
                "status": "failed",
                "error": "WSL command timeout",
                "wsl_available": False,
                "ansible_available": False
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": f"WSL check failed: {str(e)}",
                "wsl_available": False,
                "ansible_available": False
            }
    
    def create_lab_inventory(self) -> Dict[str, Any]:
        """Create lab inventory file in WSL"""
        inventory_content = """---
all:
  children:
    lab_devices:
      hosts:
        lab-router1:
          ansible_host: localhost
          ansible_port: 2221
          ansible_user: admin
          ansible_password: admin
          ansible_connection: ssh
          ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
          ansible_python_interpreter: auto_silent
          device_type: router
          
        lab-switch1:
          ansible_host: localhost
          ansible_port: 2222
          ansible_user: admin
          ansible_password: admin
          ansible_connection: ssh
          ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
          ansible_python_interpreter: auto_silent
          device_type: switch
          
        lab-firewall1:
          ansible_host: localhost
          ansible_port: 2223
          ansible_user: admin
          ansible_password: admin
          ansible_connection: ssh
          ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
          ansible_python_interpreter: auto_silent
          device_type: firewall
"""
        
        try:
            # Write inventory to WSL filesystem
            cmd = [
                "wsl", "-d", self.wsl_distro, "bash", "-c",
                f"cat > {self.inventory_path} << 'EOF'\n{inventory_content}\nEOF"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"✅ Lab inventory created at {self.inventory_path}")
                return {"status": "success", "message": "Inventory created successfully"}
            else:
                error_msg = f"Failed to create inventory: {result.stderr}"
                logger.error(f"❌ {error_msg}")
                return {"status": "failed", "error": error_msg}
                
        except Exception as e:
            error_msg = f"Exception creating inventory: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {"status": "failed", "error": error_msg}
    
    def run_connectivity_test(self) -> Dict[str, Any]:
        """Test connectivity to lab devices using Ansible"""
        try:
            # Ensure inventory exists
            inv_result = self.create_lab_inventory()
            if inv_result["status"] != "success":
                return inv_result
            
            # Run simple ping test using raw commands (no Python required)
            cmd = [
                "wsl", "-d", self.wsl_distro, "--",
                "ansible", "all", 
                "-i", self.inventory_path,
                "-m", "raw",
                "-a", "echo 'Connection successful from $(hostname)'",
                "--timeout=10"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            success_count = result.stdout.count("CHANGED | rc=0") + result.stdout.count("SUCCESS")
            total_devices = 3  # lab-router1, lab-switch1, lab-firewall1
            
            return {
                "status": "success" if success_count > 0 else "failed",
                "devices_reachable": success_count,
                "total_devices": total_devices,
                "raw_output": result.stdout,
                "errors": result.stderr if result.stderr else None
            }
            
        except subprocess.TimeoutExpired:
            return {
                "status": "failed",
                "error": "Ansible connectivity test timeout",
                "devices_reachable": 0,
                "total_devices": 3
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": f"Connectivity test failed: {str(e)}",
                "devices_reachable": 0,
                "total_devices": 3
            }
    
    def run_show_commands(self, devices: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run show commands on lab devices"""
        if devices is None:
            devices = ["lab-router1", "lab-switch1", "lab-firewall1"]
        
        try:
            # Ensure inventory exists
            inv_result = self.create_lab_inventory()
            if inv_result["status"] != "success":
                return inv_result
            
            # Create simple show commands playbook
            playbook_content = """---
- name: Show device information
  hosts: all
  gather_facts: yes
  tasks:
    - name: Show system information
      shell: |
        echo "=== SYSTEM INFO ==="
        uname -a
        echo "=== UPTIME ==="
        uptime
        echo "=== DISK USAGE ==="
        df -h
        echo "=== MEMORY ==="
        free -h
        echo "=== NETWORK ==="
        ip addr show
      register: system_output
      
    - name: Display output
      debug:
        var: system_output.stdout_lines
"""
            
            # Write playbook to WSL
            playbook_path = "/tmp/show_commands.yml"
            cmd = [
                "wsl", "-d", self.wsl_distro, "bash", "-c",
                f"cat > {playbook_path} << 'EOF'\n{playbook_content}\nEOF"
            ]
            
            subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Run the playbook
            cmd = [
                "wsl", "-d", self.wsl_distro,
                "ansible-playbook",
                "-i", self.inventory_path,
                playbook_path,
                "--timeout=30"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            return {
                "status": "success" if result.returncode == 0 else "partial",
                "output": result.stdout,
                "errors": result.stderr if result.stderr else None,
                "return_code": result.returncode
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": f"Show commands failed: {str(e)}"
            }
    
    def run_custom_playbook(self, playbook_content: str, extra_vars: Optional[Dict] = None) -> Dict[str, Any]:
        """Run a custom Ansible playbook"""
        try:
            # Ensure inventory exists
            inv_result = self.create_lab_inventory()
            if inv_result["status"] != "success":
                return inv_result
            
            # Write playbook to WSL
            playbook_path = "/tmp/custom_playbook.yml"
            cmd = [
                "wsl", "-d", self.wsl_distro, "bash", "-c",
                f"cat > {playbook_path} << 'EOF'\n{playbook_content}\nEOF"
            ]
            
            subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Build ansible-playbook command
            cmd = [
                "wsl", "-d", self.wsl_distro,
                "ansible-playbook",
                "-i", self.inventory_path,
                playbook_path
            ]
            
            # Add extra vars if provided
            if extra_vars:
                vars_str = json.dumps(extra_vars)
                cmd.extend(["--extra-vars", vars_str])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            return {
                "status": "success" if result.returncode == 0 else "failed",
                "output": result.stdout,
                "errors": result.stderr if result.stderr else None,
                "return_code": result.returncode
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": f"Custom playbook failed: {str(e)}"
            }

def get_wsl_ansible_bridge():
    """Factory function to get WSL Ansible bridge instance"""
    return WSLAnsibleBridge()
