# --- docker-container/main.tf ---

resource "docker_container" "container" {
  name         = var.name
  image        = var.image
  hostname     = var.hostname
  restart      = var.restart_policy
  network_mode = var.network_mode
  command      = var.command

  dynamic "ports" {
    for_each = var.ports
    content {
      internal = ports.value.internal
      external = ports.value.external
      protocol = ports.value.protocol
    }
  }

  dynamic "volumes" {
    for_each = var.named_volumes
    content {
      volume_name    = volumes.key
      container_path = volumes.value.container_path
      read_only      = volumes.value.read_only
    }
  }

  dynamic "volumes" {
    for_each = var.host_paths
    content {
      host_path      = volumes.key
      container_path = volumes.value.container_path
      read_only      = volumes.value.read_only
    }
  }

  dynamic "devices" {
    for_each = var.devices
    content {
      host_path      = devices.key
      container_path = devices.value.container_path
      permissions    = devices.value.permissions
    }
  }
}

