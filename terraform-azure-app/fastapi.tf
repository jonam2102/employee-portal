resource "azurerm_container_app" "fastapi" {
  name                         = "fastapi-app"
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = azurerm_resource_group.app_rg.name
  location                     = azurerm_resource_group.app_rg.location
  revision_mode                = "Single"

  template {
    container {
      name   = "fastapi"
      image  = var.fastapi_image
      cpu    = 0.5
      memory = "1Gi"

      env {
        name  = "REDIS_URL"
        value = "redis://:${var.redis_password}@redis-init:6379/0"
      }
    }

    scale {
      min_replicas = 1
      max_replicas = 2
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8000
    transport        = "auto"
  }
}
