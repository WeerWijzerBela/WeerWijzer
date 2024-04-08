terraform {
  backend "s3" {
    bucket         = "bucket-weerwijzer-container"
    key            = "terraform.tfstate"
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
