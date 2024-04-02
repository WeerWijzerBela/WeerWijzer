variable "do_token" {
  type = string
  default = "dop_v1_a22987dfe71a1b7aab2010e2d6505de178cec725ddcd9b82c29a35f78f1919d9"
}

variable "pvt_key" {
  type = string
  default = "ssh_key"

}

variable "droplet_name" {
  description = "Name of the droplet"
  default     = "weerwijzer-pool"

}

variable "domain" {
  description = "Domain name for the application"
  default     = "weerwijzer-belastingdienst.nl"
}

variable "app_image" {
  description = "Docker image for the application"
  default     = "registry.digitalocean.com/container-weerwijzer/weerwijzer-app:latest"
}
