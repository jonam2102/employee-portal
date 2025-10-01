terraform {
  required_providers {
    azapi = {
      source  = "azure/azapi"
      version = ">= 1.5.0"
    }
  }
}

provider "azapi" {}

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

resource "azapi_resource" "container_env" {
  type      = "Microsoft.App/managedEnvironments@2022-03-01"
  name      = "container-env"
  location  = var.location
  parent_id = azurerm_resource_group.rg.id

  body = jsonencode({
    properties = {
      appLogsConfiguration = {
        destination = "log-analytics"
        logAnalyticsConfiguration = {
          customerId = var.log_analytics_workspace_id
          sharedKey  = var.log_analytics_key
        }
      }
    }
  })
}

module "fastapi_app" {
  source                = "./modules/fastapi-app"
  resource_group_name   = var.resource_group_name
  location              = var.location
  container_env_id      = azapi_resource.container_env.id
    providers = {
    azapi = azure.azapi
  }
}

module "redis" {
  source                = "./modules/redis"
  resource_group_name   = var.resource_group_name
  location              = var.location
  container_env_id      = azapi_resource.container_env.id
    providers = {
    azapi = azure.azapi
  }
}

module "redis_exporter" {
  source                = "./modules/redis-exporter"
  resource_group_name   = var.resource_group_name
  location              = var.location
  container_env_id      = azapi_resource.container_env.id
    providers = {
    azapi = azure.azapi
  }
}

module "redis_init" {
  source                = "./modules/redis-init"
  resource_group_name   = var.resource_group_name
  location              = var.location
  container_env_id      = azapi_resource.container_env.id
    providers = {
    azapi = azure.azapi
  }
}
