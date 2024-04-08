terraform {
  backend "s3" {
    bucket         = "bucket-weerwijzer"
    key            = "terraform.tfstate"
    region         = "ams3"
    endpoint       = "https://bucket-weerwijzer.ams3.digitaloceanspaces.com"
    skip_region_validation = true
    secret_key = "MHcuVm9RUxVxbiAt6Dp3oItIg9zjMEM4+6aJY2EhwCA"

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

provider "kubernetes" {
  host             = digitalocean_kubernetes_cluster.weerwijzer_cluster.endpoint
  token            = digitalocean_kubernetes_cluster.weerwijzer_cluster.kube_config.0.token
  cluster_ca_certificate = base64decode(digitalocean_kubernetes_cluster.weerwijzer_cluster.kube_config.0.cluster_ca_certificate)

  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command = "doctl"
    args = ["kubernetes", "cluster", "kubeconfig", "exec-credential",
    "--version=v1beta1", digitalocean_kubernetes_cluster.weerwijzer_cluster.id]
  }
}

#provider "helm" {
#  kubernetes {
#    host  = digitalocean_kubernetes_cluster.weerwijzer_cluster.endpoint
#    token = digitalocean_kubernetes_cluster.weerwijzer_cluster.kube_config.0.token
#    cluster_ca_certificate = base64decode(
#      digitalocean_kubernetes_cluster.weerwijzer_cluster.kube_config.0.cluster_ca_certificate
#    )
#  }
#}
