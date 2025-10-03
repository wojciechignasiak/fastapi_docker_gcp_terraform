# main.tf

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.0.0"
}

provider google {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

resource "google_compute_network" "vpc_network" {
  name                    = var.vpc_network_name
  auto_create_subnetworks = true
  project                 = var.project_id
}

resource "google_compute_firewall" "app_firewall" {
  name        = var.firewall_name
  network     = google_compute_network.vpc_network.name
  project     = var.project_id

  allow {
    protocol = "tcp"
    ports    = ["22", "80"]
  }

  source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_instance" "app_server" {
  name         = var.web_app_vm_instance_name
  machine_type = "e2-micro"
  zone         = var.zone
  project      = var.project_id

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = 10
    }
  }

  network_interface {
    network = google_compute_network.vpc_network.name
    access_config {}
  }

  tags = ["http-server", "ssh-access", "fastapi-app"]

  metadata_startup_script = <<-EOF
    #!/bin/bash
    apt-get update
    apt-get install -y docker.io git curl
    systemctl enable docker
    systemctl start docker
    usermod -aG docker $USER
  EOF

  scheduling {
    automatic_restart   = true
    on_host_maintenance = "MIGRATE"
  }
}


locals {
  vm_public_ip = google_compute_instance.app_server.network_interface[0].access_config[0].nat_ip
}

resource "google_sql_database_instance" "sql_instance" {
  name             = var.database_name
  project          = var.project_id
  region           = var.region
  database_version = "POSTGRES_17"

  settings {
    tier = "db-f1-micro"
    zone = var.zone

    disk_type = "PD_SSD"
    disk_size = 10

    ip_configuration {
      ipv4_enabled = true

      authorized_networks {
        value = "${local.vm_public_ip}/32"
        name  = "fastapi-server-vm-access"
      }
    }

    backup_configuration {
      enabled            = true
      binary_log_enabled = true
      start_time         = "04:00"
    }
  }
}



# Password auto generation
resource "random_password" "database_password" {
  length  = 16
  special = true
}

# Database user for web app
resource "google_sql_user" "db_user" {
  name     = var.database_username
  instance = google_sql_database_instance.sql_instance.name
  password = random_password.database_password.result
  project  = var.project_id
}


## Secrets
resource "google_secret_manager_secret" "environment" {
  secret_id  = "ENVIRONMENT"
  replication {
    automatic = true
  }
  project = var.project_id
}

resource "google_secret_manager_secret_version" "environment" {
  secret      = google_secret_manager_secret.environment.id
  secret_data = var.environment
}


resource "google_secret_manager_secret" "database_name" {
  secret_id  = "DATABASE_NAME"
  replication {
    automatic = true
  }
  project = var.project_id
}

resource "google_secret_manager_secret_version" "database_name" {
  secret = google_secret_manager_secret.database_name.id
  secret_data = var.database_name
}


resource "google_secret_manager_secret" "database_username" {
  secret_id  = "DATABASE_USERNAME"
  replication {
    automatic = true
  }
  project = var.project_id
}

resource "google_secret_manager_secret_version" "database_username" {
  secret = google_secret_manager_secret.database_username.id
  secret_data = var.database_username
}


resource "google_secret_manager_secret" "database_password" {
  secret_id  = "DATABASE_PASSWORD"
  replication {
    automatic = true
  }
  project = var.project_id
}

resource "google_secret_manager_secret_version" "database_password" {
  secret = google_secret_manager_secret.database_password.id
  secret_data = random_password.database_password.result
}


resource "google_secret_manager_secret" "database_host" {
  secret_id  = "DATABASE_HOST"
  replication {
    automatic = true
  }
  project = var.project_id
}

resource "google_secret_manager_secret_version" "database_host" {
  secret      = google_secret_manager_secret.database_host.id
  secret_data = google_sql_database_instance.sql_instance.public_ip_address
}


resource "google_secret_manager_secret" "database_port" {
  secret_id  = "DATABASE_PORT"
  replication {
    automatic = true
  }
  project = var.project_id
}

resource "google_secret_manager_secret_version" "database_port" {
  secret      = google_secret_manager_secret.database_port.id
  secret_data = "5432"
}