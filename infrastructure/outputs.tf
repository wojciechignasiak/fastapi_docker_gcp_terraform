output "app_server_public_ip" {
  description = "Public IP address"
  value       = google_compute_instance.app_server.network_interface[0].access_config[0].nat_ip
}