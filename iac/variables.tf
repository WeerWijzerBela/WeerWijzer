variable "do_token" {
  type = string
  default = "dop_v1_a22987dfe71a1b7aab2010e2d6505de178cec725ddcd9b82c29a35f78f1919d9"
}

variable "github_token" {
  type = string
  default = "ghp_1b2b3c4d5e6f7g8h9i0j"

}
variable "top_level_domains" {
  # description = "Top level domains to create records and pods for"
  type    = list(string)
  default = ["weerwijzer-belastingdienst.nl"]
}

variable "droplet_name" {
  description = "Name of the droplet"
  default     = "weerwijzer-pool"

}

variable "domain" {
  description = "Domain name for the application"
  default     = "weerwijzer-belastingdienst.online"
}

variable "app_image" {
  description = "Docker image for the application"
  default     = "registry.digitalocean.com/container-weerwijzer/weerwijzer-app:1.04"
}
