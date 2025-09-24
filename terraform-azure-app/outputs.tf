output "fastapi_url" {
  value = azurerm_container_app.fastapi.latest_revision_fqdn
}
