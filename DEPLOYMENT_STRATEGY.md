# Lab Environment Strategy Guide
## Local Testing vs Portfolio Deployment

Based on your Network Monitoring Dashboard project, here are the optimal lab choices for each scenario:

---

## 🧪 **FOR LOCAL TESTING** (Development & Learning)

### **Recommended: Containerlab + Docker Compose**

**Why This Combination:**
- ✅ **Fast iteration** - Create/destroy labs in seconds
- ✅ **Resource efficient** - Won't slow down your development machine
- ✅ **Automation testing** - Perfect for testing your Ansible playbooks
- ✅ **Real network stacks** - Uses actual vendor network OS containers
- ✅ **Free** - No licensing costs
- ✅ **CI/CD ready** - Can automate testing in GitHub Actions

### **Local Testing Setup:**

#### 1. **Containerlab** (Primary - for Network Device Testing)
```yaml
# topology.yml
name: network-testing-lab
topology:
  nodes:
    # Cisco-like devices
    router1:
      kind: cisco_iosv
      image: cisco/iosv:latest
      mgmt_ipv4: 172.20.20.10
    
    switch1:
      kind: cisco_iosv
      image: cisco/iosv-l2:latest  
      mgmt_ipv4: 172.20.20.20
    
    # Arista devices (if testing multi-vendor)
    arista1:
      kind: arista_ceos
      image: ceos:latest
      mgmt_ipv4: 172.20.20.30
    
    # Test hosts
    host1:
      kind: linux
      image: alpine:latest
      mgmt_ipv4: 172.20.20.100

  links:
    - endpoints: ["router1:eth1", "switch1:eth1"]
    - endpoints: ["switch1:eth2", "arista1:eth1"] 
    - endpoints: ["switch1:eth3", "host1:eth0"]
```

**Commands:**
```bash
# Start lab
containerlab deploy -t topology.yml

# Test your automation
ansible-playbook -i inventory.yml configure_devices.yml

# Destroy lab
containerlab destroy -t topology.yml
```

#### 2. **Docker Compose** (Secondary - for Application Services)
```yaml
# docker-compose.yml
version: '3.8'
services:
  # Your network dashboard
  dashboard:
    build: .
    ports:
      - "8503:8503"
    environment:
      - PYTHONPATH=/app
    volumes:
      - ./data:/app/data
  
  # Mock network devices (for testing when no real devices)
  mock-device1:
    image: networkop/cx:latest
    container_name: mock-router1
    hostname: router1
    ports:
      - "2221:22"  # SSH access
    environment:
      - DEVICE_TYPE=cisco_ios
  
  # Monitoring tools
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

### **Local Testing Workflow:**
1. **Start Containerlab** → Test network automation
2. **Start Docker services** → Test application integration  
3. **Run your dashboard** → Test end-to-end functionality
4. **Iterate quickly** → Make changes, test, repeat

---

## 🌟 **FOR PORTFOLIO DEPLOYMENT** (Showcase & Demo)

### **Recommended: EVE-NG Community + Cloud VPS**

**Why This Choice:**
- ✅ **Professional appearance** - Web-based, looks enterprise-grade
- ✅ **Accessible anywhere** - Recruiters can access from any device
- ✅ **Scalable demos** - Can show complex network topologies
- ✅ **Multi-vendor showcase** - Demonstrate vendor diversity skills
- ✅ **Cloud deployment** - Shows modern infrastructure skills
- ✅ **Always available** - 24/7 portfolio access

### **Portfolio Deployment Architecture:**

#### **Cloud Setup (Recommended):**
```
┌─────────────────────────────────────────┐
│           Cloud VPS (4GB RAM+)          │
├─────────────────────────────────────────┤
│  ┌─────────────────┐ ┌─────────────────┐│
│  │    EVE-NG      │ │  Your Dashboard ││
│  │  Web Interface │ │   (Streamlit)   ││
│  │   Port 80/443  │ │   Port 8503     ││
│  └─────────────────┘ └─────────────────┘│
│              │                │        │
│  ┌─────────────────────────────────────┐│
│  │        Network Lab Topology        ││
│  │  R1 ──── SW1 ──── R2 ──── SW2     ││
│  │   │       │       │       │       ││
│  │  Host1   Host2   Host3   Host4     ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

#### **Portfolio Lab Topology:**
```yaml
# portfolio-topology.yml (for EVE-NG)
name: "Network Automation Portfolio"
description: "Demonstrates real-world network automation capabilities"

devices:
  # Core Layer
  core-r1:
    type: cisco_iosv
    mgmt_ip: 192.168.100.10
    role: core_router
    
  core-r2: 
    type: cisco_iosv
    mgmt_ip: 192.168.100.11
    role: core_router
    
  # Distribution Layer  
  dist-sw1:
    type: cisco_iosv_l2
    mgmt_ip: 192.168.100.20
    role: distribution_switch
    
  dist-sw2:
    type: cisco_iosv_l2  
    mgmt_ip: 192.168.100.21
    role: distribution_switch
    
  # Access Layer
  access-sw1:
    type: cisco_iosv_l2
    mgmt_ip: 192.168.100.30
    role: access_switch
    
  # Multi-vendor (shows diversity)
  arista-sw1:
    type: arista_veos
    mgmt_ip: 192.168.100.40
    role: access_switch
    
  # Security
  firewall1:
    type: palo_alto_vm
    mgmt_ip: 192.168.100.50
    role: firewall
    
  # Servers/Hosts
  web-server:
    type: linux_host
    mgmt_ip: 192.168.100.100
    role: web_server
    
  db-server:
    type: linux_host  
    mgmt_ip: 192.168.100.101
    role: database_server
```

### **Portfolio Cloud Providers (Ranked):**

#### **1. DigitalOcean (Recommended)**
- ✅ **$20/month** for 4GB RAM droplet
- ✅ **Simple setup** - One-click apps
- ✅ **Great docs** - Easy to follow
- ✅ **Reliable** - 99.99% uptime
- ✅ **Portfolio-friendly** - Clean, professional

#### **2. Linode (Alternative)**  
- ✅ **$24/month** for 4GB RAM
- ✅ **Better performance** - Faster CPUs
- ✅ **Documentation** - Excellent guides

#### **3. AWS EC2 (If you want AWS on resume)**
- ⚠️ **$35-50/month** for t3.medium
- ✅ **Industry standard** - Looks good on resume
- ❌ **Complex** - Steep learning curve

### **Portfolio Deployment Steps:**

#### **Phase 1: Cloud Server Setup**
```bash
# 1. Create cloud VPS (Ubuntu 22.04, 4GB RAM, 2 CPUs)
# 2. Install EVE-NG Community
wget -O - https://www.eve-ng.net/repo/install-eve.sh | bash

# 3. Install Docker for your dashboard  
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 4. Setup your dashboard
git clone https://github.com/Christmas27/Network-Monitoring.git
cd Network-Monitoring
docker-compose up -d
```

#### **Phase 2: Professional Demo Setup**
```yaml
# docker-compose.portfolio.yml
version: '3.8'
services:
  dashboard:
    build: .
    ports:
      - "8503:8503"
    environment:
      - ENV=portfolio
      - LAB_DEVICES=true
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.dashboard.rule=Host(`your-domain.com`)"
      
  reverse-proxy:
    image: traefik:v2.9
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
```

---

## 📊 **COMPARISON MATRIX**

| Use Case | Lab Type | Cost | Setup Time | Professional Look | Accessibility |
|----------|----------|------|------------|-------------------|---------------|
| **Local Testing** | Containerlab | Free | 5 min | ⭐⭐⭐ | Local only |
| **Local Testing** | Docker Compose | Free | 2 min | ⭐⭐ | Local only |
| **Portfolio Demo** | EVE-NG Cloud | $20/mo | 2 hours | ⭐⭐⭐⭐⭐ | Global |
| **Portfolio Demo** | Containerlab Cloud | $15/mo | 1 hour | ⭐⭐⭐⭐ | Global |

---

## 🎯 **MY SPECIFIC RECOMMENDATIONS FOR YOU**

### **For Local Testing:**
```bash
# Use this exact setup:
1. Install Docker Desktop
2. Use our created docker-compose.yml in lab/docker/
3. Start with: docker-compose up -d
4. Test your Ansible playbooks against containers
5. Iterate quickly without resource overhead
```

### **For Portfolio Deployment:**
```bash
# Use this exact setup:
1. Get DigitalOcean droplet ($20/month)
2. Install EVE-NG Community Edition
3. Create 5-device topology (router, switch, firewall, 2 hosts)
4. Deploy your Streamlit dashboard alongside
5. Custom domain: yourname-network-automation.com
6. Add SSL certificate (free with Let's Encrypt)
```

### **Portfolio URLs Structure:**
```
https://yourname-network-automation.com/
├── /dashboard/          → Your Streamlit app
├── /lab/               → EVE-NG web interface  
├── /docs/              → Technical documentation
├── /api/               → REST API endpoints
└── /github/            → Links to your code
```

**Bottom Line**: Use **Docker/Containerlab locally** for fast development, and **EVE-NG on cloud** for impressive portfolio demonstrations that recruiters can access anytime! 🚀
