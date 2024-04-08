variable "do_token" {
  type = string
  description = "digital ocean token to login"
}


variable "top_level_domains" {
  # description = "Top level domains to create records and pods for"
  type    = list(string)
  default = ["weerwijzer-belastingdienst.online"]
}

variable "droplet_name" {
  description = "Name of the droplet"
  default     = "weerwijzer-pool"

}

variable "domain" {
  description = "Domain name for the application"
  default     = "weerwijzer-belastingdienst.online"
}

variable "app_image_tag" {
  description = "Docker image tag for the application"
#  default     = "registry.digitalocean.com/container-weerwijzer/weerwijzer-app:1.04"
}
variable "db_password" {
  description = "Database password"
}
variable "API_KEY"{
  description = "API key"
}

variable "space_secret_key" {
  description = "Database password"
}

variable "space_access_key" {
  description = "Database password"
}
