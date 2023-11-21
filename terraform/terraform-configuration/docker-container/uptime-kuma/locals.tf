# --- template/locals.tf ---

locals {
  deployment = {
    "uptime-kuma" = {
      image          = var.image
      restart_policy = var.restart_policy
      network_mode   = var.network_mode
      command        = var.command
      ports          = var.ports
      named_volumes  = var.named_volumes
      host_paths     = var.host_paths
      devices        = var.devices
    }
  }
}