terraform {
  required_providers {
    azapi = {
      source = "azure/azapi"
    }
  }
}

resource "azapi_resource" "fastapi_app" {
  type      = "Microsoft.App/containerApps@2022-03-01"
  name      = "fastapi-app"
  location  = var.location
  parent_id = "/subscriptions/${data.azurerm_client_config.current.subscription_id}/resourceGroups/${var.resource_group_name}"
  
  body = jsonencode({
    properties = {
      managedEnvironmentId = var.container_env_id
      configuration = {
        ingress = {
          external = true
          targetPort = 8000
        }
        activeRevisionsMode = "Single"
      }
      template = {
        containers = [
          {
            name  = "fastapi"
            image = "yourregistry.azurecr.io/fastapi:latest"
            resources = {
              cpu    = 0.5
              memory = "1Gi"
            }
          }
        ]
        scale = {
          minReplicas = 1
          maxReplicas = 10
          rules = [
            {
              name = "http-scaling"
              custom = {
                type = "http"
                metadata = {
                  concurrentRequests = "5"
                }
              }
            }
          ]
        }
      }
    }
  })
}
