#!/usr/bin/env python3
"""
Virtual Lab Manager - Containerized Network Devices
Provides configurable devices for Ansible testing without complex VM setup
"""

import docker
import subprocess
import logging
import time
import json
import os
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class VirtualLabManager:
    """Manages containerized network devices for Ansible testing"""
    
    def __init__(self):
        try:
            self.docker_client = docker.from_env()
            self.docker_available = True
        except Exception as e:
            logger.warning(f"Docker not available: {e}")
            self.docker_available = False
            
        self.lab_prefix = "ansible-lab"
        self.management_network = "ansible-mgmt"
        
    def check_docker_availability(self) -> bool:
        """Check if Docker is available and running"""
        if not self.docker_available:
            return False
            
        try:
            self.docker_client.ping()
            return True
        except Exception as e:
            logger.error(f"Docker daemon not running: {e}")
            return False
    
    def create_management_network(self) -> bool:
        """Create Docker network for device management"""
        try:
            # Check if network already exists
            networks = self.docker_client.networks.list(names=[self.management_network])
            if networks:
                logger.info(f"Management network '{self.management_network}' already exists")
                return True
                
            # Create new network
            network = self.docker_client.networks.create(
                self.management_network,
                driver="bridge",
                ipam=docker.types.IPAMConfig(
                    pool_configs=[
                        docker.types.IPAMPool(
                            subnet="192.168.100.0/24",
                            gateway="192.168.100.1"
                        )
                    ]
                )
            )
            logger.info(f"Created management network: {network.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create management network: {e}")
            return False
    
    def deploy_test_lab(self, device_count: int = 3) -> Dict[str, Any]:
        """Deploy a simple test lab with Linux containers simulating network devices"""
        
        if not self.check_docker_availability():
            return {
                "status": "error",
                "message": "Docker not available. Please install Docker Desktop."
            }
        
        try:
            # Create management network
            if not self.create_management_network():
                return {
                    "status": "error", 
                    "message": "Failed to create management network"
                }
            
            devices = []
            base_ip = 192168100010  # 192.168.100.10
            
            for i in range(device_count):
                device_name = f"{self.lab_prefix}-router{i+1}"
                device_ip = f"192.168.100.{10+i}"
                
                # Check if container already exists
                try:
                    existing = self.docker_client.containers.get(device_name)
                    if existing.status == "running":
                        logger.info(f"Device {device_name} already running")
                        devices.append({
                            "name": device_name,
                            "ip": device_ip,
                            "status": "running",
                            "id": existing.id[:12]
                        })
                        continue
                    else:
                        existing.remove(force=True)
                except docker.errors.NotFound:
                    pass
                
                # Create and start new container
                container = self.docker_client.containers.run(
                    "alpine:latest",
                    name=device_name,
                    hostname=f"router{i+1}",
                    detach=True,
                    tty=True,
                    networks=[self.management_network],
                    command="/bin/sh",
                    environment={
                        "DEVICE_TYPE": "router",
                        "DEVICE_ID": str(i+1)
                    }
                )
                
                # Configure SSH and basic services
                self._configure_container_ssh(container, device_name)
                
                devices.append({
                    "name": device_name,
                    "ip": device_ip,
                    "status": "running",
                    "id": container.id[:12],
                    "type": "router"
                })
                
                logger.info(f"Deployed device: {device_name} at {device_ip}")
            
            return {
                "status": "success",
                "message": f"Deployed {len(devices)} test devices",
                "devices": devices,
                "management_network": "192.168.100.0/24"
            }
            
        except Exception as e:
            logger.error(f"Lab deployment failed: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _configure_container_ssh(self, container, device_name):
        """Configure SSH access for the container"""
        try:
            # Install and configure SSH
            commands = [
                "apk add --no-cache openssh sudo",
                "ssh-keygen -A",
                "adduser -D -s /bin/sh ansible",
                "echo 'ansible:ansible123' | chpasswd",
                "echo 'ansible ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers",
                "sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config",
                "sed -i 's/#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config",
                "/usr/sbin/sshd -D &"
            ]
            
            for cmd in commands:
                result = container.exec_run(f"/bin/sh -c '{cmd}'")
                if result.exit_code != 0 and "ssh-keygen" not in cmd:
                    logger.warning(f"Command failed in {device_name}: {cmd}")
                    
        except Exception as e:
            logger.warning(f"SSH configuration failed for {device_name}: {e}")
    
    def get_lab_status(self) -> Dict[str, Any]:
        """Get status of all lab devices"""
        if not self.check_docker_availability():
            return {"status": "error", "message": "Docker not available"}
        
        try:
            containers = self.docker_client.containers.list(
                all=True,
                filters={"name": self.lab_prefix}
            )
            
            devices = []
            for container in containers:
                device_info = {
                    "name": container.name,
                    "status": container.status,
                    "id": container.id[:12],
                    "image": container.image.tags[0] if container.image.tags else "unknown"
                }
                
                # Get IP address if running
                if container.status == "running":
                    try:
                        network_info = container.attrs['NetworkSettings']['Networks']
                        if self.management_network in network_info:
                            device_info["ip"] = network_info[self.management_network]['IPAddress']
                    except:
                        device_info["ip"] = "unknown"
                
                devices.append(device_info)
            
            return {
                "status": "success",
                "total_devices": len(devices),
                "running_devices": len([d for d in devices if d["status"] == "running"]),
                "devices": devices
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def destroy_lab(self) -> Dict[str, Any]:
        """Destroy all lab devices and cleanup"""
        if not self.check_docker_availability():
            return {"status": "error", "message": "Docker not available"}
        
        try:
            # Stop and remove containers
            containers = self.docker_client.containers.list(
                all=True,
                filters={"name": self.lab_prefix}
            )
            
            removed_count = 0
            for container in containers:
                container.remove(force=True)
                removed_count += 1
                logger.info(f"Removed container: {container.name}")
            
            # Remove management network
            try:
                network = self.docker_client.networks.get(self.management_network)
                network.remove()
                logger.info(f"Removed network: {self.management_network}")
            except docker.errors.NotFound:
                pass
            
            return {
                "status": "success",
                "message": f"Removed {removed_count} devices and cleaned up network"
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def generate_ansible_inventory(self) -> Dict[str, Any]:
        """Generate Ansible inventory for lab devices"""
        lab_status = self.get_lab_status()
        
        if lab_status["status"] != "success":
            return lab_status
        
        inventory = {
            "_meta": {"hostvars": {}},
            "all": {"children": ["lab_devices"]},
            "lab_devices": {"hosts": []}
        }
        
        for device in lab_status["devices"]:
            if device["status"] == "running" and "ip" in device:
                hostname = device["name"].replace(f"{self.lab_prefix}-", "")
                inventory["lab_devices"]["hosts"].append(hostname)
                
                inventory["_meta"]["hostvars"][hostname] = {
                    "ansible_host": device["ip"],
                    "ansible_user": "ansible", 
                    "ansible_password": "ansible123",
                    "ansible_connection": "ssh",
                    "ansible_ssh_common_args": "-o StrictHostKeyChecking=no",
                    "device_type": "linux",
                    "container_id": device["id"]
                }
        
        return {
            "status": "success",
            "inventory": inventory,
            "device_count": len(inventory["lab_devices"]["hosts"])
        }
    
    def create_test_playbook(self) -> str:
        """Create a simple test playbook for lab devices"""
        playbook_content = """---
- name: Test Lab Connectivity and Basic Configuration
  hosts: lab_devices
  gather_facts: yes
  become: yes
  
  tasks:
    - name: Check system information
      command: uname -a
      register: system_info
      
    - name: Display system information
      debug:
        msg: "Device {{ inventory_hostname }}: {{ system_info.stdout }}"
        
    - name: Create test configuration file
      copy:
        content: |
          hostname {{ inventory_hostname }}
          management_ip {{ ansible_host }}
          configured_by ansible
          timestamp {{ ansible_date_time.iso8601 }}
        dest: /tmp/device_config.txt
        
    - name: Install network tools
      package:
        name: 
          - net-tools
          - curl
          - wget
        state: present
      ignore_errors: yes
      
    - name: Create device status report
      shell: |
        echo "=== Device Status Report ===" > /tmp/status_report.txt
        echo "Hostname: $(hostname)" >> /tmp/status_report.txt
        echo "IP Address: {{ ansible_host }}" >> /tmp/status_report.txt
        echo "Uptime: $(uptime)" >> /tmp/status_report.txt
        echo "Memory: $(free -h)" >> /tmp/status_report.txt
        echo "Disk: $(df -h /)" >> /tmp/status_report.txt
        
    - name: Display configuration result
      debug:
        msg: "Configuration completed for {{ inventory_hostname }}"
"""
        
        playbook_path = os.path.join("ansible_projects", "playbooks", "test_lab_connectivity.yml")
        os.makedirs(os.path.dirname(playbook_path), exist_ok=True)
        
        with open(playbook_path, 'w') as f:
            f.write(playbook_content)
            
        return playbook_path
