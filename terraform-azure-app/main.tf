provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "app_rg" {
  name     = "USSPNXTSTACR"
  location = var.location
}

resource "azurerm_log_analytics_workspace" "logs" {
  name                = "fastapi-logs"
  location            = azurerm_resource_group.app_rg.location
  resource_group_name = azurerm_resource_group.app_rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_container_app_environment" "env" {
  name                       = "fastapi-env"
  location                   = azurerm_resource_group.app_rg.location
  resource_group_name        = azurerm_resource_group.app_rg.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.logs.id
}
