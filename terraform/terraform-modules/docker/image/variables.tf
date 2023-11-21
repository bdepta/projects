# --- docker-image/variables.tf ---

variable "image" {
  description = "Name of docker image to pull."
  type        = string
  default     = null
  validation {
    condition     = var.image != null
    error_message = "Image has to be provided. This value cannot be null."
  }
}