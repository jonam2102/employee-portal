variable "location" {
  default = "East US"
}

variable "redis_image" {
  default = "manoj/redis-init:latest"
}

variable "fastapi_image" {
  default = "manoj/fastapi-app:latest"
}

variable "redis_password" {
  default = "MySecurePassword"
}
