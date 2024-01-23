# --- docker-container/outputs.tf ---

output "container_name" {
  value       = docker_container.container[*].name
  description = "The name of the container"
}
