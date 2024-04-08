terraform {
  backend "s3" {
    bucket         = "bucket-weerwijzer-container"
    key            = "terraform.tfstate"
    region         = "ams3"
    endpoint       = "https://ams3.digitaloceanspaces.com/"
    skip_region_validation = true
#    access_key = "DO00W4P3EJPJFXH6P2UD"
#    secret_key = "fELQYN7GEM1Kxd4LHTIK3hsYWs2Vg76xtVRfaaK09Zs"
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
variable "access_key" {}
variable "secret_key" {}
