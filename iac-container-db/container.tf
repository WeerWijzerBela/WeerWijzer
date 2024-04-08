# Create a new container registry
resource "digitalocean_container_registry" "container-do" {
  name                   = "container-weerwijzer"
  subscription_tier_slug = "starter"
  region                 = "ams3"
}