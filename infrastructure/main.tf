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

provider "google" {
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
  name    = var.firewall_name
  network = google_compute_network.vpc_network.name
  project = var.project_id

  allow {
    protocol = "tcp"
    ports    = ["22", "80"]
  }

  source_ranges = ["0.0.0.0/0"]
}

resource "google_service_account" "vm_sa" {
  account_id   = "fastapi-vm-sa"
  display_name = "Service Account for FastAPI VM"
  project      = var.project_id
}

resource "google_project_iam_member" "artifact_registry_access" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.vm_sa.email}"
}

resource "google_project_iam_member" "secret_manager_access" {
    project = var.project_id
    role    = "roles/secretmanager.secretAccessor"
    member  = "serviceAccount:${google_service_account.vm_sa.email}"
  }

resource "google_compute_instance" "app_server" {
  name         = var.web_app_vm_instance_name
  machine_type = "e2-micro"
  zone         = var.zone
  project      = var.project_id
  deletion_protection = false

  boot_disk {
    initialize_params {
      image = "cos-cloud/cos-stable"
    }
  }

  network_interface {
    network = google_compute_network.vpc_network.name
    access_config {}
  }

  service_account {
    email  = google_service_account.vm_sa.email
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }


  tags = ["http-server", "ssh-access", "fastapi-app"]

  metadata = {
    "gce-container-declaration" = <<-EOT
      spec:
        containers:
          - name: fastapi-app
            image: europe-west3-docker.pkg.dev/${var.project_id}/fastapi-repo/fastapi-app:v7
            ports:
              - name: http
                containerPort: 80
            env:
              - name: ENVIRONMENT
                value: "${var.environment}"
              - name: PROJECT_ID
                value: "${var.project_id}"
        restartPolicy: Always
    EOT
  }

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
  deletion_protection = false
  database_version = "POSTGRES_16"

  settings {
    tier = "db-f1-micro"

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
      start_time         = "04:00"
    }
  }
}

resource "random_password" "database_password" {
  length  = 16
  special = true
}

resource "google_sql_user" "db_user" {
  name     = var.database_username
  instance = google_sql_database_instance.sql_instance.name
  password = random_password.database_password.result
  project  = var.project_id
}

resource "google_sql_database" "app_database" {
  name     = var.database_name
  instance = google_sql_database_instance.sql_instance.name
  project  = var.project_id
}

resource "google_secret_manager_secret" "environment" {
  secret_id = "ENVIRONMENT"
  replication {
    auto {}
  }
  project = var.project_id
}

resource "google_secret_manager_secret_version" "environment" {
  secret      = google_secret_manager_secret.environment.id
  secret_data = var.environment
}

resource "google_secret_manager_secret" "database_name" {
  secret_id = "DATABASE_NAME"
  replication {
    auto {}
  }
  project = var.project_id
}

resource "google_secret_manager_secret_version" "database_name" {
  secret      = google_secret_manager_secret.database_name.id
  secret_data = var.database_name
}

resource "google_secret_manager_secret" "database_username" {
  secret_id = "DATABASE_USERNAME"
  replication {
    auto {}
  }
  project = var.project_id
}

resource "google_secret_manager_secret_version" "database_username" {
  secret      = google_secret_manager_secret.database_username.id
  secret_data = var.database_username
}

resource "google_secret_manager_secret" "database_password" {
  secret_id = "DATABASE_PASSWORD"
  replication {
    auto {}
  }
  project = var.project_id
}

resource "google_secret_manager_secret_version" "database_password" {
  secret      = google_secret_manager_secret.database_password.id
  secret_data = random_password.database_password.result
}

resource "google_secret_manager_secret" "database_host" {
  secret_id = "DATABASE_HOST"
  replication {
    auto {}
  }
  project = var.project_id
}

resource "google_secret_manager_secret_version" "database_host" {
  secret      = google_secret_manager_secret.database_host.id
  secret_data = google_sql_database_instance.sql_instance.public_ip_address
}

resource "google_secret_manager_secret" "database_port" {
  secret_id = "DATABASE_PORT"
  replication {
    auto {}
  }
  project = var.project_id
}

resource "google_secret_manager_secret_version" "database_port" {
  secret      = google_secret_manager_secret.database_port.id
  secret_data = "5432"
}

