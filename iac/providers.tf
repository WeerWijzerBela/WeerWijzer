terraform {
  backend "s3" {
    bucket         = "bucket-weerwijzer"
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
    grafana = {
      source  = "grafana/grafana"
      version = "~> 2.15.0"  # Vervang x.y.z door de gewenste versie
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

provider "helm" {
  kubernetes {
    host  = digitalocean_kubernetes_cluster.weerwijzer_cluster.endpoint
    token = digitalocean_kubernetes_cluster.weerwijzer_cluster.kube_config.0.token
    cluster_ca_certificate = base64decode(
      digitalocean_kubernetes_cluster.weerwijzer_cluster.kube_config.0.cluster_ca_certificate
    )
  }
}
provider "grafana" {
  url  = "https://weerwijzer.grafana.net/"
  auth = "glsa_q2eh9n9kXHsOM5Okas0NkNMwCz6ZTOHl_33c4c34a"
}
