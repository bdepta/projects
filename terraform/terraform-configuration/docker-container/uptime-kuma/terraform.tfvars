# --- template/terraform.tfvars ---

image          = "louislam/uptime-kuma"
restart_policy = "unless-stopped"
network_mode   = "bridge"
ports = [
  {
    internal = 3001
    external = 3001
    protocol = "tcp"
}]
named_volumes = {
  "uptime-kuma" = {
    container_path = "/app/data"
    read_only      = false
    create         = true
  }
}