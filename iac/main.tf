resource "digitalocean_kubernetes_cluster" "weerwijzer_cluster" {
  name    = "weerwijzer-cluster"
  region  = "ams3"  # Update to your preferred region
  version = "latest" # Automatically selects the latest version
  registry_integration = true

  node_pool {
    name       = var.droplet_name
    size       = "s-2vcpu-2gb" # Adjust based on your needs
    node_count = 1
    auto_scale = true
    min_nodes  = 1
    max_nodes  = 3
  }
}

resource "null_resource" "registry_credentials" {
  # Triggers this resource to be recreated, reapplying the secret, whenever the cluster ID changes
  triggers = {
    cluster_id = digitalocean_kubernetes_cluster.weerwijzer_cluster.id
  }

  provisioner "local-exec" {
    command = "doctl auth init --access-token ${var.do_token}"
  }

  provisioner "local-exec" {
    command = "doctl registry kubernetes-manifest | kubectl apply -f -"
  }


  depends_on = [
    digitalocean_kubernetes_cluster.weerwijzer_cluster,
  ]
}

resource "kubernetes_deployment" "weerwijzer_app" {
  depends_on = [
    null_resource.registry_credentials
  ]
  metadata {
    name = "weerwijzer-app"
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        app = "weerwijzer-app"
      }
    }

    template {
      metadata {
        labels = {
          app = "weerwijzer-app"
        }
      }


      spec {
        container {
          name  = "weerwijzer-app"
          image = var.app_image
          port {
            container_port = 80
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "weerwijzer_lb" {
  metadata {
    name = "weerwijzer-lb"
  }

  spec {
    selector = {
      app = "weerwijzer-app"
    }

    port {
      port        = 80
      target_port = 80
    }

    type = "LoadBalancer"
  }
}


# resource "digitalocean_record" "app_dns" {
#   depends_on = [ digitalocean_loadbalancer.public ]
#   domain = var.domain
#   type   = "A"
#   name   = "@" # Root domain, use something else for subdomains
#   value  = [kubernetes_service.weerwijzer_lb.ip]
#   ttl    = 3600
# }

