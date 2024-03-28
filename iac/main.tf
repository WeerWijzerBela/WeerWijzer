terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
    token = var.do_token
}


resource "digitalocean_kubernetes_cluster" "terraform" {
    name    = "terraform"
    region  = "ams3"
    version = "1.29.1-do.0"
    node_pool {
        name       = "worker-pool"
        size       = "s-1vcpu-2gb"
        auto_scale = true
        min_nodes = 1
        max_nodes = 3
    }
  
}