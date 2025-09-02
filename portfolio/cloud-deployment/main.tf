
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
