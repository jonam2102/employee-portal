terraform {
  required_providers {
    azapi = {
      source = "azure/azapi"
    }
  }
}

resource "azapi_resource" "redis_init_app" {
  type      = "Microsoft.App/containerApps@2022-03-01"
  name      = "redis-init"
  location  = var.location
  parent_id = "/subscriptions/${data.azurerm_client_config.current.subscription_id}/resourceGroups/${var.resource_group_name}"

  body = jsonencode({
    properties = {
      managedEnvironmentId = var.container_env_id
      configuration = {
        activeRevisionsMode = "Single"
      }
      template = {
        containers = [
          {
            name  = "redis-init"
            image = "yourregistry.azurecr.io/redis-init:latest"
            resources = {
              cpu    = 0.25
              memory = "0.5Gi"
            }
          }
        ]
      }
    }
  })
}
