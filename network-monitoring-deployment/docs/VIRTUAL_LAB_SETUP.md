# 🧪 Virtual Lab Setup Guide
## Configurable Network Devices for Ansible Testing

Since Catalyst Center sandbox has authentication issues and read-only limitations, here are practical alternatives for testing Ansible automation:

---

## 🏆 Option 1: EVE-NG Community Edition (Recommended)

### Why EVE-NG?
- ✅ **Free Community Edition** available
- ✅ **Multi-vendor support** (Cisco, Arista, Juniper, etc.)
- ✅ **Web-based interface** - no additional software needed
- ✅ **Built-in topology designer**
- ✅ **Snapshot functionality** for easy lab reset
- ✅ **Better resource management** than GNS3

### Installation Steps:

#### Step 1: Download EVE-NG Community
```bash
# Download from: https://www.eve-ng.net/index.php/download/
# Choose "EVE Community Edition"
# Install on VMware/VirtualBox (4GB+ RAM recommended)
```

#### Step 2: Basic Configuration
```bash
# After installation, access web interface at:
# http://[EVE-NG-IP]
# Default login: admin / eve
```

#### Step 3: Add Device Images
```bash
# Upload Cisco IOSv images to:
# /opt/unetlab/addons/qemu/vios-adventerprisek9-m/

# For testing, you can use:
# - Cisco IOSv (vios-adventerprisek9-m)
# - Cisco IOSvL2 (viosl2-adventerprisek9-m) 
# - Arista vEOS (available free with registration)
```

### Sample Lab Topology:
```
Internet
    |
[EVE-NG Host]
    |
Management Network (192.168.100.0/24)
    |
    +-- Router1 (192.168.100.10)  
    +-- Router2 (192.168.100.11)
    +-- Switch1 (192.168.100.12)
    +-- Switch2 (192.168.100.13)
```

---

## 🐳 Option 2: Containerlab (Lightweight Alternative)

### Why Containerlab?
- ✅ **Docker-based** - very lightweight
- ✅ **Easy to script and automate**
- ✅ **Perfect for CI/CD integration**
- ✅ **Fast startup/teardown**
- ✅ **No VM overhead**

### Installation:
```bash
# Install Docker first, then:
curl -sL https://containerlab.dev/setup | sudo bash

# Or with package manager:
sudo apt install containerlab  # Ubuntu/Debian
brew install containerlab      # macOS
```

### Sample Lab Configuration:
```yaml
# lab.yml
name: ansible-test-lab

topology:
  nodes:
    router1:
      kind: cisco_iosv
      image: cisco/iosv:latest
      mgmt_ipv4: 192.168.100.10
      
    router2:
      kind: cisco_iosv  
      image: cisco/iosv:latest
      mgmt_ipv4: 192.168.100.11
      
    switch1:
      kind: cisco_iosvl2
      image: cisco/iosvl2:latest
      mgmt_ipv4: 192.168.100.12

  links:
    - endpoints: ["router1:e0/0", "router2:e0/0"]
    - endpoints: ["router1:e0/1", "switch1:e0/1"]
```

### Deploy Lab:
```bash
# Start the lab
sudo containerlab deploy -t lab.yml

# Access devices
ssh admin@192.168.100.10

# Destroy lab when done
sudo containerlab destroy -t lab.yml
```

---

## 🎮 Option 3: Cisco DevNet Sandbox with Simulation Mode

### Hybrid Approach:
Since DevNet has authentication issues, we can use it for **read-only discovery** and simulate write operations:

```python
# Enhanced Ansible Manager with Simulation Mode
class AnsibleManager:
    def __init__(self, simulation_mode=True):
        self.simulation_mode = simulation_mode
        
    def run_playbook(self, playbook_name, **kwargs):
        if self.simulation_mode:
            return self._simulate_playbook_execution(playbook_name)
        else:
            return self._real_playbook_execution(playbook_name, **kwargs)
            
    def _simulate_playbook_execution(self, playbook_name):
        """Simulate playbook execution with realistic results"""
        return {
            "status": "successful",
            "changes": ["hostname configured", "ntp servers updated"],
            "failed_tasks": [],
            "execution_time": "45.2s",
            "note": "SIMULATED EXECUTION - No actual changes made"
        }
```

---

## 🚀 Option 4: Cloud-Based Virtual Lab

### AWS/Azure Network Simulation:
```bash
# Use cloud instances with nested virtualization
# Cost: ~$20-50/month for development lab
# Benefit: Always accessible, no local resource usage
```

### Digital Ocean Droplets:
```bash
# Cheaper alternative: $10-20/month
# Run EVE-NG or Containerlab on cloud VPS
# Access via web interface
```

---

## 🎯 Recommended Implementation Plan

### Phase 1: Quick Start (This Session)
```bash
# Install Containerlab (5 minutes)
curl -sL https://containerlab.dev/setup | bash

# Create simple 2-device lab
cat > test-lab.yml << EOF
name: ansible-test
topology:
  nodes:
    router1:
      kind: linux
      image: alpine:latest
      mgmt_ipv4: 192.168.100.10
    router2:  
      kind: linux
      image: alpine:latest
      mgmt_ipv4: 192.168.100.11
EOF

# Deploy and test
sudo containerlab deploy -t test-lab.yml
```

### Phase 2: Full Network Lab (Next Session)
1. Set up EVE-NG with proper Cisco images
2. Create realistic network topology
3. Configure management access
4. Test Ansible connectivity

### Phase 3: Integration (Final Phase)  
1. Connect Streamlit app to virtual lab
2. Real playbook execution testing
3. Configuration backup/restore
4. Compliance checking

---

## 🔧 Ansible Configuration for Virtual Lab

### Create Ansible Inventory:
```yaml
# inventory/lab_hosts.yml
all:
  children:
    lab_devices:
      hosts:
        router1:
          ansible_host: 192.168.100.10
          ansible_network_os: ios
          ansible_user: admin
          ansible_password: admin
          ansible_connection: network_cli
        router2:
          ansible_host: 192.168.100.11  
          ansible_network_os: ios
          ansible_user: admin
          ansible_password: admin
          ansible_connection: network_cli
```

### Test Connectivity Playbook:
```yaml
# playbooks/test_connectivity.yml
---
- name: Test Lab Connectivity
  hosts: lab_devices
  gather_facts: no
  tasks:
    - name: Get device facts
      ios_facts:
      register: device_info
      
    - name: Display device information
      debug:
        msg: "Device {{ inventory_hostname }}: {{ device_info.ansible_facts.ansible_net_version }}"
```

---

## 🛠️ Integration with Your Streamlit App

### Update Device Manager:
```python
# Add lab device detection
def detect_lab_devices(self):
    """Detect available lab devices"""
    lab_devices = []
    
    # Check containerlab status
    try:
        result = subprocess.run(['containerlab', 'inspect'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            # Parse containerlab output for running labs
            pass
    except:
        pass
        
    return lab_devices
```

### Add Lab Management Tab:
```python
# In streamlit_app.py
elif selected_page == "🧪 Lab Management":
    st.header("🧪 Virtual Lab Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Lab Status")
        # Show running labs, device count, etc.
        
    with col2:  
        st.subheader("🚀 Quick Actions")
        if st.button("🏗️ Deploy Test Lab"):
            # Deploy containerlab configuration
            pass
            
        if st.button("🗑️ Destroy Lab"):
            # Clean up lab resources
            pass
```

---

## 🏃‍♂️ Quick Start Command

Let's start with the simplest option that works immediately:

```bash
# Option 1: Linux containers for initial testing
docker run -d --name test-device1 --hostname router1 \
  -p 2201:22 alpine:latest /bin/sh -c "while true; do sleep 30; done"

# Option 2: Use existing VM if available
# Create simple test environment in your local VM
```

Which option would you like to implement first? I recommend starting with **Containerlab** for immediate testing, then setting up **EVE-NG** for a full network lab experience.
