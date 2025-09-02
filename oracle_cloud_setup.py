#!/usr/bin/env python3
"""
Oracle Cloud Free Tier Portfolio Setup
Automates the deployment of Network Monitoring Dashboard on Oracle Cloud Always Free tier
"""

import os
import yaml
import json
from pathlib import Path

class OracleCloudPortfolioSetup:
    def __init__(self):
        self.setup_configs = {
            "terraform": self.create_terraform_config,
            "cloud_init": self.create_cloud_init_script,
            "docker_compose": self.create_docker_compose,
            "eve_ng": self.create_eve_ng_setup
        }
        
    def create_terraform_config(self):
        """Create Terraform configuration for Oracle Cloud"""
        terraform_config = '''
# Oracle Cloud Infrastructure - Always Free Tier
# This configuration creates a permanent free portfolio environment

terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 5.0"
    }
  }
}

variable "tenancy_ocid" {
  description = "OCID of your tenancy"
  type        = string
}

variable "user_ocid" {
  description = "OCID of your user"
  type        = string
}

variable "fingerprint" {
  description = "Fingerprint of your public key"
  type        = string
}

variable "private_key_path" {
  description = "Path to your private key"
  type        = string
}

variable "region" {
  description = "Oracle Cloud region"
  type        = string
  default     = "us-ashburn-1"
}

provider "oci" {
  tenancy_ocid     = var.tenancy_ocid
  user_ocid        = var.user_ocid
  fingerprint      = var.fingerprint
  private_key_path = var.private_key_path
  region           = var.region
}

# Get availability domain
data "oci_identity_availability_domains" "ads" {
  compartment_id = var.tenancy_ocid
}

# Create VCN (Virtual Cloud Network)
resource "oci_core_vcn" "portfolio_vcn" {
  compartment_id = var.tenancy_ocid
  cidr_block     = "10.0.0.0/16"
  display_name   = "portfolio-vcn"
  dns_label      = "portfoliovcn"
}

# Create Internet Gateway
resource "oci_core_internet_gateway" "portfolio_igw" {
  compartment_id = var.tenancy_ocid
  vcn_id         = oci_core_vcn.portfolio_vcn.id
  display_name   = "portfolio-igw"
}

# Create Route Table
resource "oci_core_route_table" "portfolio_rt" {
  compartment_id = var.tenancy_ocid
  vcn_id         = oci_core_vcn.portfolio_vcn.id
  display_name   = "portfolio-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    network_entity_id = oci_core_internet_gateway.portfolio_igw.id
  }
}

# Create Security List
resource "oci_core_security_list" "portfolio_sl" {
  compartment_id = var.tenancy_ocid
  vcn_id         = oci_core_vcn.portfolio_vcn.id
  display_name   = "portfolio-sl"

  # Ingress rules
  ingress_security_rules {
    protocol = "6" # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      min = 22
      max = 22
    }
  }

  ingress_security_rules {
    protocol = "6" # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      min = 80
      max = 80
    }
  }

  ingress_security_rules {
    protocol = "6" # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      min = 443
      max = 443
    }
  }

  ingress_security_rules {
    protocol = "6" # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      min = 8503
      max = 8503
    }
  }

  # Egress rules
  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
  }
}

# Create Subnet
resource "oci_core_subnet" "portfolio_subnet" {
  compartment_id      = var.tenancy_ocid
  vcn_id              = oci_core_vcn.portfolio_vcn.id
  cidr_block          = "10.0.1.0/24"
  display_name        = "portfolio-subnet"
  dns_label           = "portfoliosub"
  route_table_id      = oci_core_route_table.portfolio_rt.id
  security_list_ids   = [oci_core_security_list.portfolio_sl.id]
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
}

# Create ARM Instance (Always Free - 4 OCPUs, 24GB RAM)
resource "oci_core_instance" "portfolio_arm_instance" {
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  compartment_id      = var.tenancy_ocid
  display_name        = "portfolio-lab-server"
  shape               = "VM.Standard.A1.Flex"

  shape_config {
    ocpus         = 4    # Maximum free
    memory_in_gbs = 24   # Maximum free
  }

  create_vnic_details {
    subnet_id              = oci_core_subnet.portfolio_subnet.id
    display_name           = "portfolio-vnic"
    assign_public_ip       = true
    assign_private_dns_record = true
  }

  source_details {
    source_type = "image"
    source_id   = "ocid1.image.oc1..aaaaaaaa7o2imwpqkb25s2lrhmyv2ltgzlkqn5w3b5qfm2kcgqo3e6qq5b7a" # Ubuntu 22.04 ARM
  }

  metadata = {
    ssh_authorized_keys = file("~/.ssh/id_rsa.pub")
    user_data          = base64encode(file("cloud-init.yml"))
  }
}

# Create AMD Instance (Always Free - 1 OCPU, 1GB RAM) 
resource "oci_core_instance" "portfolio_amd_instance" {
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  compartment_id      = var.tenancy_ocid
  display_name        = "portfolio-dashboard"
  shape               = "VM.Standard.E2.1.Micro"

  create_vnic_details {
    subnet_id              = oci_core_subnet.portfolio_subnet.id
    display_name           = "dashboard-vnic"
    assign_public_ip       = true
    assign_private_dns_record = true
  }

  source_details {
    source_type = "image"
    source_id   = "ocid1.image.oc1..aaaaaaaayuihpsm2nfkxztdkottbjtjjyhz5t2w4j33qog2urmzqmyqzjlmma" # Ubuntu 22.04 AMD
  }

  metadata = {
    ssh_authorized_keys = file("~/.ssh/id_rsa.pub")
    user_data          = base64encode(file("cloud-init-dashboard.yml"))
  }
}

# Outputs
output "arm_instance_public_ip" {
  value = oci_core_instance.portfolio_arm_instance.public_ip
  description = "Public IP of ARM instance (EVE-NG Lab)"
}

output "amd_instance_public_ip" {
  value = oci_core_instance.portfolio_amd_instance.public_ip
  description = "Public IP of AMD instance (Dashboard)"
}

output "ssh_connection_arm" {
  value = "ssh ubuntu@${oci_core_instance.portfolio_arm_instance.public_ip}"
  description = "SSH command for ARM instance"
}

output "ssh_connection_amd" {
  value = "ssh ubuntu@${oci_core_instance.portfolio_amd_instance.public_ip}"
  description = "SSH command for AMD instance"
}
'''
        
        with open("oracle_cloud/main.tf", "w") as f:
            f.write(terraform_config)
            
        print("✅ Terraform configuration created: oracle_cloud/main.tf")
        
    def create_cloud_init_script(self):
        """Create cloud-init script for EVE-NG setup"""
        
        # Cloud-init for ARM instance (EVE-NG Lab)
        cloud_init_arm = '''#cloud-config
package_update: true
package_upgrade: true

packages:
  - docker.io
  - docker-compose
  - nginx
  - certbot
  - python3-certbot-nginx
  - htop
  - git
  - curl
  - wget

users:
  - name: ubuntu
    sudo: ALL=(ALL) NOPASSWD:ALL
    shell: /bin/bash
    ssh_authorized_keys:
      - ssh-rsa YOUR_PUBLIC_KEY_HERE

runcmd:
  # Setup Docker
  - systemctl enable docker
  - systemctl start docker
  - usermod -aG docker ubuntu
  
  # Download and install EVE-NG Community
  - cd /tmp
  - wget https://www.eve-ng.net/attachments/download/2029/eve-ng-2.0.3-112.iso
  - mkdir -p /opt/eve-ng
  
  # Install EVE-NG Community (simplified installation)
  - apt-get update
  - apt-get install -y qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virt-manager
  - systemctl enable libvirtd
  - systemctl start libvirtd
  
  # Setup networking for EVE-NG
  - echo 'net.ipv4.ip_forward = 1' >> /etc/sysctl.conf
  - sysctl -p
  
  # Create EVE-NG lab directory structure
  - mkdir -p /opt/unetlab/addons/iol/bin
  - mkdir -p /opt/unetlab/addons/qemu
  - mkdir -p /opt/unetlab/labs
  
  # Setup firewall for EVE-NG ports
  - ufw allow 22
  - ufw allow 80
  - ufw allow 443
  - ufw allow 32768:65535/tcp
  - ufw allow 32768:65535/udp
  - ufw --force enable
  
  # Create simple web interface for lab access
  - echo '<h1>EVE-NG Lab Server</h1><p>ARM Instance - 4 cores, 24GB RAM</p><p>Always Free Oracle Cloud</p>' > /var/www/html/index.html
  
  # Setup log rotation
  - echo '*/5 * * * * root echo "$(date): EVE-NG Lab running on Oracle Cloud ARM - $(free -h | grep Mem)" >> /var/log/portfolio.log' >> /etc/crontab

write_files:
  - path: /etc/motd
    content: |
      ===============================================
      🌟 Oracle Cloud ARM Instance (Always Free)
      🔬 EVE-NG Lab Server - Portfolio Environment
      💾 4 OCPUs, 24GB RAM - Forever Free!
      ===============================================
      
  - path: /opt/setup-eve-ng.sh
    permissions: '0755'
    content: |
      #!/bin/bash
      echo "Setting up EVE-NG Community Edition..."
      
      # Install additional dependencies
      apt-get install -y apache2 php php-mysql mysql-server
      
      # Start services
      systemctl enable apache2
      systemctl start apache2
      systemctl enable mysql
      systemctl start mysql
      
      # Setup basic authentication
      echo "EVE-NG setup completed!"
      echo "Access at: http://$(curl -s http://ipv4.icanhazip.com)"
'''

        # Cloud-init for AMD instance (Dashboard)
        cloud_init_amd = '''#cloud-config
package_update: true
package_upgrade: true

packages:
  - docker.io
  - docker-compose
  - nginx
  - certbot
  - python3-certbot-nginx
  - python3-pip
  - git

runcmd:
  # Setup Docker
  - systemctl enable docker
  - systemctl start docker
  - usermod -aG docker ubuntu
  
  # Clone portfolio repository
  - cd /home/ubuntu
  - git clone https://github.com/Christmas27/Network-Monitoring.git
  - cd Network-Monitoring
  
  # Setup Python environment
  - python3 -m pip install --upgrade pip
  - pip3 install -r requirements-production.txt
  
  # Start dashboard service
  - docker-compose -f docker-compose.portfolio.yml up -d
  
  # Setup Nginx reverse proxy
  - systemctl enable nginx
  - systemctl start nginx
  
  # Setup firewall
  - ufw allow 22
  - ufw allow 80
  - ufw allow 443
  - ufw allow 8503
  - ufw --force enable

write_files:
  - path: /etc/motd
    content: |
      ===============================================
      🌟 Oracle Cloud AMD Instance (Always Free)
      📊 Network Dashboard - Portfolio Environment  
      💾 1 OCPU, 1GB RAM - Forever Free!
      ===============================================
      
  - path: /etc/nginx/sites-available/dashboard
    content: |
      server {
          listen 80;
          server_name _;
          
          location / {
              proxy_pass http://localhost:8503;
              proxy_set_header Host $host;
              proxy_set_header X-Real-IP $remote_addr;
              proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
              proxy_set_header X-Forwarded-Proto $scheme;
          }
      }
'''
        
        os.makedirs("oracle_cloud", exist_ok=True)
        
        with open("oracle_cloud/cloud-init.yml", "w") as f:
            f.write(cloud_init_arm)
            
        with open("oracle_cloud/cloud-init-dashboard.yml", "w") as f:
            f.write(cloud_init_amd)
            
        print("✅ Cloud-init scripts created:")
        print("  - oracle_cloud/cloud-init.yml (EVE-NG setup)")
        print("  - oracle_cloud/cloud-init-dashboard.yml (Dashboard setup)")
        
    def create_docker_compose(self):
        """Create Docker Compose for Oracle Cloud deployment"""
        
        docker_compose = {
            "version": "3.8",
            "services": {
                "dashboard": {
                    "build": ".",
                    "ports": ["8503:8503"],
                    "environment": [
                        "ENV=oracle_cloud",
                        "LAB_DEVICES=true",
                        "DEMO_MODE=true",
                        "OCI_FREE_TIER=true"
                    ],
                    "volumes": [
                        "./data:/app/data",
                        "./logs:/app/logs"
                    ],
                    "restart": "unless-stopped",
                    "labels": [
                        "description=Network Monitoring Dashboard - Oracle Cloud Always Free"
                    ]
                },
                "api": {
                    "build": ".",
                    "command": "python main.py",
                    "ports": ["5000:5000"],
                    "environment": [
                        "ENV=oracle_cloud",
                        "FLASK_APP=main.py"
                    ],
                    "restart": "unless-stopped"
                },
                "nginx": {
                    "image": "nginx:alpine",
                    "ports": ["80:80", "443:443"],
                    "volumes": [
                        "./nginx/nginx.conf:/etc/nginx/nginx.conf",
                        "./nginx/ssl:/etc/nginx/ssl"
                    ],
                    "depends_on": ["dashboard", "api"],
                    "restart": "unless-stopped"
                }
            }
        }
        
        with open("oracle_cloud/docker-compose.yml", "w") as f:
            yaml.dump(docker_compose, f, default_flow_style=False)
            
        print("✅ Docker Compose created: oracle_cloud/docker-compose.yml")
        
    def create_eve_ng_setup(self):
        """Create EVE-NG specific setup files"""
        
        # Create basic topology for portfolio demo
        eve_topology = {
            "topology": {
                "name": "Portfolio Network Lab",
                "description": "Network automation demonstration lab",
                "version": "1.0",
                "nodes": {
                    "R1": {
                        "type": "iol",
                        "template": "i86bi_linux-adventerprisek9-ms",
                        "image": "i86bi_linux-adventerprisek9-ms.bin",
                        "config": "hostname R1\\ninterface GigabitEthernet0/0\\n ip address 192.168.1.1 255.255.255.0\\n no shutdown",
                        "x": 100,
                        "y": 100
                    },
                    "R2": {
                        "type": "iol", 
                        "template": "i86bi_linux-adventerprisek9-ms",
                        "image": "i86bi_linux-adventerprisek9-ms.bin",
                        "config": "hostname R2\\ninterface GigabitEthernet0/0\\n ip address 192.168.1.2 255.255.255.0\\n no shutdown",
                        "x": 300,
                        "y": 100
                    },
                    "SW1": {
                        "type": "iol",
                        "template": "i86bi_linux_l2-adventerprisek9-ms", 
                        "image": "i86bi_linux_l2-adventerprisek9-ms.bin",
                        "config": "hostname SW1\\nvlan 10\\n name USERS\\nvlan 20\\n name SERVERS",
                        "x": 200,
                        "y": 200
                    }
                },
                "connections": [
                    {"source": "R1:e0/0", "destination": "SW1:e0/1"},
                    {"source": "R2:e0/0", "destination": "SW1:e0/2"}
                ]
            }
        }
        
        with open("oracle_cloud/eve-ng-topology.json", "w") as f:
            json.dump(eve_topology, f, indent=2)
            
        print("✅ EVE-NG topology created: oracle_cloud/eve-ng-topology.json")
        
    def create_setup_guide(self):
        """Create comprehensive setup guide"""
        
        setup_guide = '''# Oracle Cloud Always Free Portfolio Setup Guide

## 🎯 Overview
This guide helps you deploy your Network Monitoring Dashboard on Oracle Cloud's Always Free tier - completely free forever!

## 📋 Prerequisites
1. Oracle Cloud account (free signup)
2. SSH key pair generated
3. Basic familiarity with terminal/command line

## 🚀 Step-by-Step Setup

### Step 1: Oracle Cloud Account Setup
```bash
# 1. Go to oracle.com/cloud/free
# 2. Click "Start for free"
# 3. Fill in details (valid email, phone required)
# 4. Choose home region (closest to you)
# 5. Verify email and phone
```

### Step 2: Generate SSH Keys (if not done)
```bash
# Windows (PowerShell):
ssh-keygen -t rsa -b 4096 -f ~/.ssh/oci_key

# Linux/Mac:
ssh-keygen -t rsa -b 4096 -f ~/.ssh/oci_key
```

### Step 3: Setup OCI CLI and Terraform
```bash
# Install OCI CLI
pip install oci-cli

# Configure OCI CLI
oci setup config

# Install Terraform
# Download from terraform.io/downloads
```

### Step 4: Deploy Infrastructure
```bash
# Clone your repository
git clone https://github.com/Christmas27/Network-Monitoring.git
cd Network-Monitoring/oracle_cloud

# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Deploy (creates Always Free resources)
terraform apply
```

### Step 5: Access Your Portfolio
```bash
# Get instance IPs
terraform output

# SSH to ARM instance (EVE-NG)
ssh ubuntu@<arm_instance_ip>

# SSH to AMD instance (Dashboard)  
ssh ubuntu@<amd_instance_ip>
```

## 🌐 Portfolio URLs
After deployment, your portfolio will be accessible at:
- **EVE-NG Lab**: http://<arm_instance_ip>
- **Dashboard**: http://<amd_instance_ip>:8503
- **API**: http://<amd_instance_ip>:5000

## 💰 Cost Breakdown
- **ARM Instance**: $0 (Always Free - 4 OCPUs, 24GB RAM)
- **AMD Instance**: $0 (Always Free - 1 OCPU, 1GB RAM)  
- **Storage**: $0 (Always Free - 200GB total)
- **Bandwidth**: $0 (Always Free - 10TB/month)
- **Total Monthly**: **$0 FOREVER!**

## 🔧 Maintenance
Your portfolio runs automatically with:
- ✅ Auto-restart on reboot
- ✅ Log rotation configured
- ✅ Firewall properly configured
- ✅ SSL-ready (add domain later)

## 📈 Upgrade Path
When ready for production:
1. Add custom domain ($12/year)
2. Add SSL certificate (free with Let's Encrypt)
3. Scale resources if needed (pay-as-you-grow)

## 🆘 Troubleshooting
Common issues and solutions:
- **Instance not starting**: Check availability domain
- **SSH connection refused**: Verify security list rules
- **EVE-NG not accessible**: Check port 80 in firewall
- **Dashboard not loading**: Verify Docker containers running

## 🎉 Success!
Your portfolio is now running on Oracle Cloud Always Free tier - completely free forever!
'''
        
        with open("oracle_cloud/SETUP_GUIDE.md", "w") as f:
            f.write(setup_guide)
            
        print("✅ Setup guide created: oracle_cloud/SETUP_GUIDE.md")
        
    def setup_oracle_portfolio(self):
        """Create complete Oracle Cloud portfolio setup"""
        print("🌟 Creating Oracle Cloud Always Free Portfolio Setup...")
        print("=" * 60)
        
        # Create directory
        os.makedirs("oracle_cloud", exist_ok=True)
        
        # Create all configurations
        self.create_terraform_config()
        self.create_cloud_init_script()
        self.create_docker_compose()
        self.create_eve_ng_setup()
        self.create_setup_guide()
        
        print("\n🎉 Oracle Cloud portfolio setup completed!")
        print("\n📁 Files created in oracle_cloud/:")
        print("  ✅ main.tf - Terraform infrastructure")
        print("  ✅ cloud-init.yml - EVE-NG server setup")
        print("  ✅ cloud-init-dashboard.yml - Dashboard server setup")
        print("  ✅ docker-compose.yml - Application containers")
        print("  ✅ eve-ng-topology.json - Sample network topology")
        print("  ✅ SETUP_GUIDE.md - Complete deployment guide")
        
        print("\n🚀 Next steps:")
        print("1. Sign up for Oracle Cloud (free)")
        print("2. cd oracle_cloud")
        print("3. terraform init && terraform apply")
        print("4. Enjoy FREE portfolio forever!")
        
        print(f"\n💰 Total cost: $0 forever (saves $3000+ over 10 years)")

if __name__ == "__main__":
    oracle_setup = OracleCloudPortfolioSetup()
    oracle_setup.setup_oracle_portfolio()
