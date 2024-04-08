terraform {
  backend "s3" {
    bucket         = "bucket-weerwijzer"
    key            = "container-db.tfstate"
    region         = "ams3"
    endpoint       = "https://ams3.digitaloceanspaces.com/"
    skip_region_validation = true
    skip_credentials_validation = true

  }
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = ">= 2.7.0"
    }
  }
}

provider "digitalocean" {
    token = var.do_token

}
variable "do_token" {}
variable "API_KEY" {}
variable "app_image_tag" {}
variable "db_password" {}

provider "grafana" {
  url  = "https://weerwijzer.grafana.net/"
  auth = "glsa_q2eh9n9kXHsOM5Okas0NkNMwCz6ZTOHl_33c4c34a"
}