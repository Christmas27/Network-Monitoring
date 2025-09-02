#!/usr/bin/env python3
"""
Network Lab Environment Setup
Creates virtual network topologies for testing automation scripts
"""

import os
import subprocess
import yaml
import json
from pathlib import Path

class NetworkLabManager:
    def __init__(self):
        self.lab_configs = {
            "containerlab": self.setup_containerlab,
            "docker": self.setup_docker_lab,
            "eve-ng": self.setup_eve_ng,
            "physical": self.setup_physical_lab
        }
    
    def setup_containerlab(self):
        """Setup Containerlab environment - Best for network automation"""
        print("🔬 Setting up Containerlab environment...")
        
        # Create containerlab topology
        topology = {
            "name": "network-automation-lab",
            "topology": {
                "nodes": {
                    "spine1": {
                        "kind": "nokia_srlinux",
                        "image": "ghcr.io/nokia/srlinux:latest"
                    },
                    "leaf1": {
                        "kind": "nokia_srlinux", 
                        "image": "ghcr.io/nokia/srlinux:latest"
                    },
                    "leaf2": {
                        "kind": "nokia_srlinux",
                        "image": "ghcr.io/nokia/srlinux:latest"
                    },
                    "host1": {
                        "kind": "linux",
                        "image": "alpine:latest"
                    },
                    "host2": {
                        "kind": "linux", 
                        "image": "alpine:latest"
                    }
                },
                "links": [
                    {"endpoints": ["spine1:e1-1", "leaf1:e1-1"]},
                    {"endpoints": ["spine1:e1-2", "leaf2:e1-1"]},
                    {"endpoints": ["leaf1:e1-2", "host1:eth0"]},
                    {"endpoints": ["leaf2:e1-2", "host2:eth0"]}
                ]
            }
        }
        
        # Save topology file
        with open("lab/containerlab/topology.yml", "w") as f:
            yaml.dump(topology, f, default_flow_style=False)
        
        print("✅ Containerlab topology created: lab/containerlab/topology.yml")
        print("🚀 To start: containerlab deploy -t lab/containerlab/topology.yml")
        
    def setup_docker_lab(self):
        """Setup Docker-based network lab - Lightweight option"""
        print("🐳 Setting up Docker network lab...")
        
        # Create docker-compose for network simulation
        docker_compose = {
            "version": "3.8",
            "services": {
                "router1": {
                    "image": "networkop/cx:latest",
                    "container_name": "lab-router1",
                    "cap_add": ["NET_ADMIN"],
                    "networks": ["mgmt", "link1"],
                    "volumes": ["./configs:/configs"]
                },
                "router2": {
                    "image": "networkop/cx:latest", 
                    "container_name": "lab-router2",
                    "cap_add": ["NET_ADMIN"],
                    "networks": ["mgmt", "link1", "link2"]
                },
                "switch1": {
                    "image": "networkop/cx:latest",
                    "container_name": "lab-switch1", 
                    "cap_add": ["NET_ADMIN"],
                    "networks": ["mgmt", "link2"]
                }
            },
            "networks": {
                "mgmt": {"driver": "bridge"},
                "link1": {"driver": "bridge"}, 
                "link2": {"driver": "bridge"}
            }
        }
        
        os.makedirs("lab/docker", exist_ok=True)
        with open("lab/docker/docker-compose.yml", "w") as f:
            yaml.dump(docker_compose, f, default_flow_style=False)
            
        print("✅ Docker lab created: lab/docker/docker-compose.yml")
        print("🚀 To start: cd lab/docker && docker-compose up -d")
        
    def setup_eve_ng(self):
        """Setup EVE-NG lab configuration"""
        print("🔬 Setting up EVE-NG lab configuration...")
        
        eve_lab = {
            "lab_info": {
                "name": "Network Automation Lab",
                "description": "Lab for testing Ansible/Python automation",
                "author": "Network Engineer",
                "version": "1.0"
            },
            "nodes": {
                "R1": {
                    "type": "iol",
                    "template": "i86bi_linux-adventerprisek9-ms",
                    "config": "R1_initial.cfg"
                },
                "R2": {
                    "type": "iol", 
                    "template": "i86bi_linux-adventerprisek9-ms",
                    "config": "R2_initial.cfg"
                },
                "SW1": {
                    "type": "iol",
                    "template": "i86bi_linux_l2-adventerprisek9-ms", 
                    "config": "SW1_initial.cfg"
                }
            },
            "connections": [
                {"source": "R1:e0/0", "target": "SW1:e0/1"},
                {"source": "R2:e0/0", "target": "SW1:e0/2"},
                {"source": "R1:e0/1", "target": "R2:e0/1"}
            ]
        }
        
        os.makedirs("lab/eve-ng", exist_ok=True)
        with open("lab/eve-ng/lab_config.json", "w") as f:
            json.dump(eve_lab, f, indent=2)
            
        print("✅ EVE-NG lab config created: lab/eve-ng/lab_config.json")
        
    def setup_physical_lab(self):
        """Setup physical lab device inventory"""
        print("🔧 Setting up physical lab configuration...")
        
        physical_inventory = {
            "lab_devices": {
                "routers": [
                    {
                        "name": "lab-r1",
                        "ip": "192.168.100.10", 
                        "type": "cisco_ios",
                        "username": "admin",
                        "password": "admin",
                        "location": "Lab Rack 1"
                    },
                    {
                        "name": "lab-r2",
                        "ip": "192.168.100.11",
                        "type": "cisco_ios", 
                        "username": "admin",
                        "password": "admin",
                        "location": "Lab Rack 1"
                    }
                ],
                "switches": [
                    {
                        "name": "lab-sw1",
                        "ip": "192.168.100.20",
                        "type": "cisco_ios",
                        "username": "admin", 
                        "password": "admin",
                        "location": "Lab Rack 1"
                    }
                ]
            }
        }
        
        os.makedirs("lab/physical", exist_ok=True)
        with open("lab/physical/inventory.yml", "w") as f:
            yaml.dump(physical_inventory, f, default_flow_style=False)
            
        print("✅ Physical lab inventory created: lab/physical/inventory.yml")
        
    def create_lab_environment(self, lab_type="docker"):
        """Create the specified lab environment"""
        print(f"🚀 Creating {lab_type} lab environment...")
        
        # Create main lab directory
        os.makedirs("lab", exist_ok=True)
        
        if lab_type in self.lab_configs:
            self.lab_configs[lab_type]()
        else:
            print(f"❌ Unknown lab type: {lab_type}")
            print(f"Available types: {list(self.lab_configs.keys())}")
            
    def list_available_labs(self):
        """List all available lab types"""
        print("📋 Available Lab Types:")
        print("1. containerlab - Professional network simulation (Recommended)")
        print("2. docker - Lightweight containerized lab")
        print("3. eve-ng - Enterprise lab platform")
        print("4. physical - Physical device lab setup")

if __name__ == "__main__":
    lab_manager = NetworkLabManager()
    
    print("🔬 Network Lab Environment Setup")
    print("=" * 40)
    
    lab_manager.list_available_labs()
    
    # Create Docker lab by default (easiest to start with)
    lab_manager.create_lab_environment("docker")
    lab_manager.create_lab_environment("physical")
    
    print("\n🎉 Lab environments created!")
    print("\n📚 Next steps:")
    print("1. Install Docker: https://docs.docker.com/get-docker/")
    print("2. Start lab: cd lab/docker && docker-compose up -d")
    print("3. Test connectivity: docker exec -it lab-router1 /bin/bash")
    print("4. Run automation scripts against lab devices")
