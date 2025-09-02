#!/usr/bin/env python3
"""
Quick Lab Deployment Script
Demonstrates how to create configurable devices for Ansible testing

Since Catalyst Center sandbox has authentication issues, this script provides
immediate alternatives for testing Ansible automation.
"""

import subprocess
import time
import json
import os

def check_docker():
    """Check if Docker is available"""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker available: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker not found")
            return False
    except FileNotFoundError:
        print("❌ Docker not installed. Please install Docker Desktop.")
        return False

def deploy_simple_lab():
    """Deploy a simple 3-device lab using Alpine Linux containers"""
    
    if not check_docker():
        return False
    
    print("🚀 Deploying simple SSH-enabled lab for Ansible testing...")
    
    # Create Docker network for lab
    print("📡 Creating management network...")
    try:
        subprocess.run([
            'docker', 'network', 'create', 
            '--subnet=192.168.100.0/24',
            '--gateway=192.168.100.1',
            'ansible-lab-net'
        ], check=True, capture_output=True)
        print("✅ Network created: ansible-lab-net")
    except subprocess.CalledProcessError:
        print("⚠️ Network already exists or creation failed")
    
    # Deploy 3 test devices
    devices = []
    for i in range(1, 4):
        device_name = f"lab-router{i}"
        device_ip = f"192.168.100.{9+i}"
        
        print(f"🐳 Starting {device_name}...")
        
        try:
            # Remove existing container if any
            subprocess.run(['docker', 'rm', '-f', device_name], 
                         capture_output=True)
            
            # Start new container with SSH
            subprocess.run([
                'docker', 'run', '-d',
                '--name', device_name,
                '--hostname', f"router{i}",
                '--network', 'ansible-lab-net',
                '--ip', device_ip,
                '-p', f'220{i}:22',  # SSH port mapping
                'alpine:latest',
                '/bin/sh', '-c', 
                '''
                apk add --no-cache openssh sudo &&
                ssh-keygen -A &&
                adduser -D -s /bin/sh ansible &&
                echo "ansible:ansible123" | chpasswd &&
                echo "ansible ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers &&
                sed -i "s/#PermitRootLogin.*/PermitRootLogin yes/" /etc/ssh/sshd_config &&
                sed -i "s/#PasswordAuthentication.*/PasswordAuthentication yes/" /etc/ssh/sshd_config &&
                /usr/sbin/sshd -D
                '''
            ], check=True, capture_output=True)
            
            devices.append({
                "name": device_name,
                "ip": device_ip,
                "ssh_port": f"220{i}",
                "status": "running"
            })
            
            print(f"✅ {device_name} deployed at {device_ip}")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to deploy {device_name}: {e}")
    
    # Wait for SSH to be ready
    print("⏳ Waiting for SSH services to start...")
    time.sleep(10)
    
    # Generate Ansible inventory
    inventory = generate_ansible_inventory(devices)
    
    print("\n🎉 Lab deployment completed!")
    print(f"📊 Devices deployed: {len(devices)}")
    print("📋 Device details:")
    for device in devices:
        print(f"   • {device['name']}: {device['ip']} (SSH port {device['ssh_port']})")
    
    print(f"\n📄 Ansible inventory saved to: ansible_inventory.yml")
    
    return True

def generate_ansible_inventory(devices):
    """Generate Ansible inventory for lab devices"""
    
    inventory = {
        "all": {
            "children": {
                "lab_devices": {
                    "hosts": {}
                }
            }
        }
    }
    
    for device in devices:
        host_name = device["name"]
        inventory["all"]["children"]["lab_devices"]["hosts"][host_name] = {
            "ansible_host": device["ip"],
            "ansible_user": "ansible",
            "ansible_password": "ansible123", 
            "ansible_connection": "ssh",
            "ansible_ssh_common_args": "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null",
            "device_type": "linux_container",
            "ssh_port": device["ssh_port"]
        }
    
    # Save inventory to file
    os.makedirs("ansible_projects/inventory", exist_ok=True)
    inventory_file = "ansible_projects/inventory/lab_hosts.yml"
    
    import yaml
    with open(inventory_file, 'w') as f:
        yaml.dump(inventory, f, default_flow_style=False)
    
    return inventory_file

def create_test_playbook():
    """Create a simple test playbook"""
    
    playbook_content = """---
- name: Test Lab Connectivity and Configuration
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
        
    - name: Install basic network tools
      package:
        name: 
          - net-tools
          - curl
          - wget
        state: present
      ignore_errors: yes
      
    - name: Create device configuration file
      copy:
        content: |
          # Device Configuration
          hostname {{ inventory_hostname }}
          management_ip {{ ansible_host }}
          device_type {{ device_type }}
          configured_by ansible
          last_update {{ ansible_date_time.iso8601 }}
        dest: /tmp/device_config.txt
        
    - name: Generate device status report
      shell: |
        echo "=== Device Status Report ===" > /tmp/status_report.txt
        echo "Hostname: $(hostname)" >> /tmp/status_report.txt
        echo "IP Address: {{ ansible_host }}" >> /tmp/status_report.txt
        echo "Kernel: $(uname -r)" >> /tmp/status_report.txt
        echo "Uptime: $(uptime)" >> /tmp/status_report.txt
        echo "Memory: $(free -h | head -2)" >> /tmp/status_report.txt
        echo "Disk Usage: $(df -h / | tail -1)" >> /tmp/status_report.txt
        
    - name: Read status report
      slurp:
        src: /tmp/status_report.txt
      register: status_report
      
    - name: Display status report
      debug:
        msg: "{{ status_report.content | b64decode }}"
"""
    
    os.makedirs("ansible_projects/playbooks", exist_ok=True)
    playbook_file = "ansible_projects/playbooks/test_lab.yml"
    
    with open(playbook_file, 'w') as f:
        f.write(playbook_content)
    
    print(f"📄 Test playbook created: {playbook_file}")
    return playbook_file

def test_ansible_connectivity():
    """Test Ansible connectivity to lab devices"""
    
    print("🧪 Testing Ansible connectivity...")
    
    # Create simple test command
    test_command = [
        'ansible', 'lab_devices', 
        '-i', 'ansible_projects/inventory/lab_hosts.yml',
        '-m', 'ping',
        '--ask-pass'
    ]
    
    print("📋 Run this command to test connectivity:")
    print(f"   {' '.join(test_command)}")
    print("   (Password: ansible123)")
    
    # Alternative: use ansible-playbook
    print("\n📋 Or run the test playbook:")
    print("   ansible-playbook -i ansible_projects/inventory/lab_hosts.yml ansible_projects/playbooks/test_lab.yml --ask-pass")

def cleanup_lab():
    """Clean up lab environment"""
    
    print("🧹 Cleaning up lab environment...")
    
    # Stop and remove containers
    for i in range(1, 4):
        device_name = f"lab-router{i}"
        try:
            subprocess.run(['docker', 'rm', '-f', device_name], 
                         capture_output=True, check=True)
            print(f"✅ Removed {device_name}")
        except subprocess.CalledProcessError:
            print(f"⚠️ {device_name} not found or already removed")
    
    # Remove network
    try:
        subprocess.run(['docker', 'network', 'rm', 'ansible-lab-net'],
                     capture_output=True, check=True)
        print("✅ Removed network: ansible-lab-net")
    except subprocess.CalledProcessError:
        print("⚠️ Network not found or already removed")
    
    print("🎉 Lab cleanup completed!")

def main():
    """Main menu for lab management"""
    
    print("🧪 Virtual Lab Manager for Ansible Testing")
    print("=" * 50)
    print("Since Catalyst Center has authentication issues, this provides")
    print("configurable devices for real Ansible testing.")
    print()
    
    while True:
        print("\n📋 Available Actions:")
        print("1. 🚀 Deploy Lab (3 SSH-enabled containers)")
        print("2. 🧪 Test Ansible Connectivity") 
        print("3. 📄 Create Test Playbook")
        print("4. 🧹 Cleanup Lab")
        print("5. 📊 Check Lab Status")
        print("6. ❌ Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == "1":
            deploy_simple_lab()
            create_test_playbook()
        elif choice == "2":
            test_ansible_connectivity()
        elif choice == "3":
            create_test_playbook()
        elif choice == "4":
            cleanup_lab()
        elif choice == "5":
            check_lab_status()
        elif choice == "6":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Please try again.")

def check_lab_status():
    """Check current lab status"""
    
    print("📊 Checking lab status...")
    
    try:
        # Check containers
        result = subprocess.run([
            'docker', 'ps', '--filter', 'name=lab-router', 
            '--format', 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
        ], capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            print("✅ Running lab devices:")
            print(result.stdout)
        else:
            print("⚠️ No lab devices running")
            
        # Check network
        net_result = subprocess.run([
            'docker', 'network', 'ls', '--filter', 'name=ansible-lab-net'
        ], capture_output=True, text=True)
        
        if 'ansible-lab-net' in net_result.stdout:
            print("✅ Management network: ansible-lab-net exists")
        else:
            print("⚠️ Management network not found")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking status: {e}")

if __name__ == "__main__":
    main()
