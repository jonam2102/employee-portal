resource "azurerm_container_app" "redis" {
  name                         = "redis-init"
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = azurerm_resource_group.app_rg.name
  location                     = azurerm_resource_group.app_rg.location
  revision_mode                = "Single"

  template {
    container {
      name   = "redis"
      image  = var.redis_image
      cpu    = 0.25
      memory = "0.5Gi"

      command = [ "redis-server", "--requirepass", var.redis_password, "--protected-mode", "no" ]
    }

    scale {
      min_replicas = 1
      max_replicas = 1
    }
  }

  ingress {
    external_enabled = false
    target_port      = 6379
  }
}
