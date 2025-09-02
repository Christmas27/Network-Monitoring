#!/usr/bin/env python3
"""
Portfolio Lab Deployment Helper
Automates the setup of network labs for portfolio demonstrations
"""

import os
import yaml
import json
import subprocess
from pathlib import Path

class PortfolioLabManager:
    def __init__(self):
        self.deployment_configs = {
            "local_testing": self.setup_local_testing,
            "portfolio_cloud": self.setup_portfolio_cloud,
            "hybrid": self.setup_hybrid
        }
        
    def setup_local_testing(self):
        """Setup optimized local testing environment"""
        print("🧪 Setting up LOCAL TESTING environment...")
        
        # Create Containerlab topology for local testing
        containerlab_topology = {
            "name": "network-testing-lab",
            "mgmt": {
                "network": "mgmt-net",
                "ipv4_subnet": "172.20.20.0/24"
            },
            "topology": {
                "nodes": {
                    "router1": {
                        "kind": "linux",
                        "image": "networkop/cx:latest",
                        "mgmt_ipv4": "172.20.20.10",
                        "env": {
                            "DEVICE_TYPE": "cisco_ios",
                            "HOSTNAME": "LAB-R1"
                        },
                        "ports": ["2221:22"]
                    },
                    "switch1": {
                        "kind": "linux", 
                        "image": "networkop/cx:latest",
                        "mgmt_ipv4": "172.20.20.20",
                        "env": {
                            "DEVICE_TYPE": "cisco_ios",
                            "HOSTNAME": "LAB-SW1"
                        },
                        "ports": ["2222:22"]
                    },
                    "router2": {
                        "kind": "linux",
                        "image": "networkop/cx:latest", 
                        "mgmt_ipv4": "172.20.20.30",
                        "env": {
                            "DEVICE_TYPE": "cisco_ios",
                            "HOSTNAME": "LAB-R2"
                        },
                        "ports": ["2223:22"]
                    },
                    "host1": {
                        "kind": "linux",
                        "image": "alpine:latest",
                        "mgmt_ipv4": "172.20.20.100"
                    }
                },
                "links": [
                    {"endpoints": ["router1:eth1", "switch1:eth1"]},
                    {"endpoints": ["switch1:eth2", "router2:eth1"]},
                    {"endpoints": ["switch1:eth3", "host1:eth0"]}
                ]
            }
        }
        
        # Create directory structure
        os.makedirs("portfolio/local-testing", exist_ok=True)
        
        # Save Containerlab topology
        with open("portfolio/local-testing/topology.yml", "w") as f:
            yaml.dump(containerlab_topology, f, default_flow_style=False)
            
        # Create Docker Compose for application services
        docker_compose_local = {
            "version": "3.8",
            "services": {
                "dashboard": {
                    "build": ".",
                    "ports": ["8503:8503"],
                    "environment": [
                        "PYTHONPATH=/app",
                        "ENV=local_testing",
                        "LAB_MODE=true"
                    ],
                    "volumes": [
                        "./data:/app/data",
                        "./logs:/app/logs"
                    ],
                    "depends_on": ["prometheus"]
                },
                "prometheus": {
                    "image": "prom/prometheus:latest",
                    "ports": ["9090:9090"],
                    "volumes": ["./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml"]
                },
                "grafana": {
                    "image": "grafana/grafana:latest",
                    "ports": ["3000:3000"],
                    "environment": [
                        "GF_SECURITY_ADMIN_PASSWORD=admin123"
                    ]
                }
            }
        }
        
        with open("portfolio/local-testing/docker-compose.yml", "w") as f:
            yaml.dump(docker_compose_local, f, default_flow_style=False)
            
        # Create test automation inventory
        test_inventory = {
            "lab_devices": {
                "hosts": {
                    "lab-r1": {
                        "ansible_host": "172.20.20.10",
                        "ansible_user": "admin",
                        "ansible_password": "admin",
                        "ansible_connection": "ansible.netcommon.network_cli",
                        "ansible_network_os": "cisco.ios.ios"
                    },
                    "lab-sw1": {
                        "ansible_host": "172.20.20.20", 
                        "ansible_user": "admin",
                        "ansible_password": "admin",
                        "ansible_connection": "ansible.netcommon.network_cli",
                        "ansible_network_os": "cisco.ios.ios"
                    },
                    "lab-r2": {
                        "ansible_host": "172.20.20.30",
                        "ansible_user": "admin", 
                        "ansible_password": "admin",
                        "ansible_connection": "ansible.netcommon.network_cli",
                        "ansible_network_os": "cisco.ios.ios"
                    }
                }
            }
        }
        
        with open("portfolio/local-testing/inventory.yml", "w") as f:
            yaml.dump(test_inventory, f, default_flow_style=False)
            
        print("✅ Local testing environment created!")
        print("📁 Files created:")
        print("  - portfolio/local-testing/topology.yml (Containerlab)")
        print("  - portfolio/local-testing/docker-compose.yml (Services)")
        print("  - portfolio/local-testing/inventory.yml (Ansible)")
        print("")
        print("🚀 Quick start:")
        print("  cd portfolio/local-testing")
        print("  containerlab deploy -t topology.yml")
        print("  docker-compose up -d")
        
    def setup_portfolio_cloud(self):
        """Setup cloud-based portfolio environment"""
        print("🌟 Setting up PORTFOLIO CLOUD environment...")
        
        # Create cloud deployment configuration
        cloud_config = {
            "cloud_deployment": {
                "provider": "digitalocean",
                "instance_type": "s-2vcpu-4gb",
                "region": "nyc1",
                "os": "ubuntu-22-04-x64"
            },
            "services": {
                "eve_ng": {
                    "port": 80,
                    "ssl": True,
                    "domain": "lab.yourportfolio.com"
                },
                "dashboard": {
                    "port": 8503,
                    "ssl": True, 
                    "domain": "dashboard.yourportfolio.com"
                },
                "api": {
                    "port": 5000,
                    "ssl": True,
                    "domain": "api.yourportfolio.com"
                }
            }
        }
        
        # Create Terraform configuration for cloud deployment
        terraform_config = """
# Digital Ocean Portfolio Infrastructure
terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

variable "do_token" {}

provider "digitalocean" {
  token = var.do_token
}

resource "digitalocean_droplet" "portfolio_lab" {
  image  = "ubuntu-22-04-x64"
  name   = "network-portfolio-lab"
  region = "nyc1"
  size   = "s-2vcpu-4gb"
  
  user_data = file("cloud-init.yml")
  
  tags = ["portfolio", "network-automation", "lab"]
}

resource "digitalocean_domain" "portfolio" {
  name       = "yourportfolio.com"
  ip_address = digitalocean_droplet.portfolio_lab.ipv4_address
}

resource "digitalocean_record" "lab" {
  domain = digitalocean_domain.portfolio.name
  type   = "A"
  name   = "lab"
  value  = digitalocean_droplet.portfolio_lab.ipv4_address
}

resource "digitalocean_record" "dashboard" {
  domain = digitalocean_domain.portfolio.name
  type   = "A" 
  name   = "dashboard"
  value  = digitalocean_droplet.portfolio_lab.ipv4_address
}

output "droplet_ip" {
  value = digitalocean_droplet.portfolio_lab.ipv4_address
}
"""
        
        # Create cloud-init script
        cloud_init = """
#cloud-config
package_update: true
packages:
  - docker.io
  - docker-compose
  - nginx
  - certbot
  - python3-certbot-nginx

runcmd:
  # Install EVE-NG
  - wget -O - https://www.eve-ng.net/repo/install-eve.sh | bash
  
  # Setup Docker
  - systemctl enable docker
  - systemctl start docker
  - usermod -aG docker ubuntu
  
  # Clone portfolio repository
  - cd /home/ubuntu
  - git clone https://github.com/Christmas27/Network-Monitoring.git
  - cd Network-Monitoring
  
  # Start services
  - docker-compose -f docker-compose.portfolio.yml up -d
  
  # Setup SSL certificates
  - certbot --nginx -d lab.yourportfolio.com --non-interactive --agree-tos -m your@email.com
  - certbot --nginx -d dashboard.yourportfolio.com --non-interactive --agree-tos -m your@email.com
"""
        
        # Create Docker Compose for portfolio
        docker_compose_portfolio = {
            "version": "3.8",
            "services": {
                "dashboard": {
                    "build": ".",
                    "ports": ["8503:8503"],
                    "environment": [
                        "ENV=portfolio",
                        "LAB_DEVICES=true", 
                        "DEMO_MODE=true"
                    ],
                    "labels": [
                        "traefik.enable=true",
                        "traefik.http.routers.dashboard.rule=Host(`dashboard.yourportfolio.com`)",
                        "traefik.http.routers.dashboard.tls.certresolver=letsencrypt"
                    ]
                },
                "reverse_proxy": {
                    "image": "traefik:v2.9",
                    "ports": ["80:80", "443:443"],
                    "volumes": [
                        "/var/run/docker.sock:/var/run/docker.sock",
                        "./traefik:/etc/traefik"
                    ]
                },
                "api": {
                    "build": ".",
                    "command": "python main.py",
                    "ports": ["5000:5000"],
                    "environment": ["ENV=portfolio"],
                    "labels": [
                        "traefik.enable=true",
                        "traefik.http.routers.api.rule=Host(`api.yourportfolio.com`)"
                    ]
                }
            }
        }
        
        # Create directories
        os.makedirs("portfolio/cloud-deployment", exist_ok=True)
        
        # Save files
        with open("portfolio/cloud-deployment/config.yml", "w") as f:
            yaml.dump(cloud_config, f, default_flow_style=False)
            
        with open("portfolio/cloud-deployment/main.tf", "w") as f:
            f.write(terraform_config)
            
        with open("portfolio/cloud-deployment/cloud-init.yml", "w") as f:
            f.write(cloud_init)
            
        with open("portfolio/cloud-deployment/docker-compose.portfolio.yml", "w") as f:
            yaml.dump(docker_compose_portfolio, f, default_flow_style=False)
            
        print("✅ Portfolio cloud environment created!")
        print("📁 Files created:")
        print("  - portfolio/cloud-deployment/main.tf (Terraform)")
        print("  - portfolio/cloud-deployment/cloud-init.yml (Server setup)")
        print("  - portfolio/cloud-deployment/docker-compose.portfolio.yml")
        print("")
        print("🚀 Deployment steps:")
        print("  1. Get DigitalOcean API token")
        print("  2. cd portfolio/cloud-deployment")
        print("  3. terraform init && terraform plan")
        print("  4. terraform apply")
        
    def setup_hybrid(self):
        """Setup hybrid local + cloud environment"""
        print("🔄 Setting up HYBRID environment...")
        self.setup_local_testing()
        self.setup_portfolio_cloud()
        print("✅ Hybrid environment ready!")
        
    def create_portfolio_lab(self, deployment_type="local_testing"):
        """Create the specified portfolio lab environment"""
        print(f"🚀 Creating {deployment_type} portfolio lab...")
        
        if deployment_type in self.deployment_configs:
            self.deployment_configs[deployment_type]()
        else:
            print(f"❌ Unknown deployment type: {deployment_type}")
            print(f"Available types: {list(self.deployment_configs.keys())}")
            
    def generate_portfolio_docs(self):
        """Generate documentation for portfolio showcase"""
        print("📝 Generating portfolio documentation...")
        
        portfolio_readme = """
# Network Automation Portfolio

## 🌟 Live Demo
- **Dashboard**: https://dashboard.yourportfolio.com
- **Lab Environment**: https://lab.yourportfolio.com  
- **API Documentation**: https://api.yourportfolio.com/docs

## 🛠️ Technologies Demonstrated
- **Frontend**: Streamlit (Python)
- **Backend**: Flask REST API
- **Network Automation**: Ansible, NAPALM, Netmiko
- **Monitoring**: Prometheus, Grafana
- **Containerization**: Docker, Docker Compose
- **Infrastructure**: Terraform, Cloud Deployment
- **Lab Environment**: EVE-NG, Containerlab

## 🔬 Lab Topology
- **Core Routers**: 2x Cisco ISR
- **Distribution Switches**: 2x Cisco Catalyst
- **Access Switches**: 2x Cisco + 1x Arista (Multi-vendor)
- **Security**: Palo Alto Firewall
- **Servers**: Web, Database, Monitoring

## 🎯 Key Features
- Real-time network monitoring
- Automated device configuration
- Multi-vendor support
- Security compliance scanning
- Performance analytics
- REST API integration

## 📊 Metrics Tracked
- Device availability
- Interface utilization
- Configuration compliance
- Security posture
- Performance trends
"""
        
        with open("portfolio/README.md", "w") as f:
            f.write(portfolio_readme)
            
        print("✅ Portfolio documentation created!")

if __name__ == "__main__":
    portfolio_manager = PortfolioLabManager()
    
    print("🎯 Portfolio Lab Deployment Helper")
    print("=" * 40)
    print()
    print("Available deployment types:")
    print("1. local_testing - Fast development & testing")
    print("2. portfolio_cloud - Professional portfolio showcase") 
    print("3. hybrid - Both local testing + cloud portfolio")
    print()
    
    # Create both environments
    portfolio_manager.create_portfolio_lab("local_testing")
    print()
    portfolio_manager.create_portfolio_lab("portfolio_cloud")
    print()
    portfolio_manager.generate_portfolio_docs()
    
    print("\n🎉 Portfolio lab environments created!")
    print("\n📋 Next steps:")
    print("Local Testing:")
    print("  cd portfolio/local-testing && containerlab deploy -t topology.yml")
    print("\nPortfolio Cloud:")
    print("  cd portfolio/cloud-deployment && terraform apply")
    print("\n📚 Documentation: portfolio/README.md")
