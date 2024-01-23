# --- docker-container/variables.tf ---

variable "name" {
  description = "Custom container name"
  type        = string
  default     = null
  validation {
    condition     = length(split("_", var.name)[0]) > 4
    error_message = "Container name must be at least 4 characters long."
  }
}

variable "image" {
  description = "Name of docker image to pull."
  type        = string
  default     = null
  validation {
    condition     = var.image != null
    error_message = "Image has to be provided. This value cannot be null."
  }
}
variable "hostname" {
  description = "Set docker hostname"
  type        = string
  default     = null
  validation {
    condition     = length(var.hostname) > 4
    error_message = "Container name must be at least 4 characters long."
  }
}
variable "restart_policy" {
  description = "Restart policy. Default: no"
  type        = string
  default     = "no"
  validation {
    condition     = contains(["no", "on-failure", "always", "unless-stopped"], var.restart_policy)
    error_message = "Valid values for restart_policy: no, on-failure, always, unless-stopped. Documentation: https://docs.docker.com/config/containers/start-containers-automatically/ ."
  }
}
variable "network_mode" {
  description = "Specify a custom network mode"
  type        = string
  default     = "bridge"
  validation {
    condition     = contains(["bridge", "host", "overlay", "ipvlan", "macvlan", "none"], var.network_mode)
    error_message = "Valid values for restart_policy: bridge, host, overlay, ipvlan, macvlan, none. Documentation: https://docs.docker.com/network/drivers/ ."
  }
}
variable "command" {
  description = "Override the default command"
  type        = list(string)
  default     = null
}
variable "ports" {
  description = "Expose ports"
  type = list(object({
    internal = number
    external = number
    protocol = string
  }))
  default = null
}
variable "named_volumes" {
  description = "Mount named volumes"
  type = map(object({
    container_path = string
    read_only      = bool
    create         = bool
  }))
  default = {}
}
variable "host_paths" {
  description = "Mount host paths"
  type = map(object({
    container_path = string
    read_only      = bool
  }))
  default = {}
}
variable "devices" {
  description = "Device mappings"
  type = map(object({
    container_path = string
    permissions    = string
  }))
  default = {}
}