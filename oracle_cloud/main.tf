
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
