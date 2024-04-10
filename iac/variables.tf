variable "do_token" {
  type = string
  description = "digital ocean token to login"
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
  default     = "weerwijzer-belastingdienst.nl"
}

variable "app_image_tag" {
  description = "Docker image tag for the application"
}
variable "db_password" {
  description = "Database password"
}


variable "db_user" {
  description = "Database user"
}
variable "db_host" {
  description = "Database host"
}
variable "db_name" {
  description = "Database name"
}
variable "db_port" {
  description = "Database port"
}

