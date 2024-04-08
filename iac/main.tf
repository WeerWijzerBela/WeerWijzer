resource "digitalocean_kubernetes_cluster" "weerwijzer_cluster" {
  name    = "weerwijzer-cluster"
  region  = "ams3"  # Update to your preferred region
  version = "1.29.1-do.0" # Update to your preferred version
  registry_integration = true

  node_pool {
    name       = var.droplet_name
    size       = "s-2vcpu-2gb" # Adjust based on your needs
    node_count = 1
    auto_scale = true
    min_nodes  = 1
    max_nodes  = 3
    tags = ["weerwijzer-node-lb"]
  }
}

resource "kubernetes_deployment" "weerwijzer_app" {
  depends_on = [digitalocean_kubernetes_cluster.weerwijzer_cluster]
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
          image = "registry.digitalocean.com/container-weerwijzer/weerwijzer-app:${var.app_image_tag}"
          env {
            name  = "DB_HOST"
            value = "mysqldb-weerwijzer-do-user-15988447-0.c.db.ondigitalocean.com"
          }
          env {
            name  = "DB_NAME"
            value = "defaultdb"
          }
          env {
            name  = "DB_PORT"
            value = 25060
          }
          env {
            name  = "DB_USER"
            value = "doadmin"
          }
          env {
            name  = "DB_PASSWORD"
            value = var.db_password
          }
          env {
            name  = "API_KEY"
            value = var.API_KEY
          }
          port {
            container_port = 8080
          }
        }
      }
    }
  }
}

resource "digitalocean_domain" "top_level_domains" {
  depends_on = [digitalocean_kubernetes_cluster.weerwijzer_cluster]
  name     = var.domain
}

resource "digitalocean_record" "a_records" {
  depends_on = [digitalocean_domain.top_level_domains]
  domain   = var.domain
  type     = "A"
  ttl      = 60
  name     = "@"
  value = kubernetes_service.weerwijzer_app_service.status.0.load_balancer.0.ingress.0.ip
}

resource "digitalocean_record" "cname_redirects" {
  depends_on = [digitalocean_domain.top_level_domains]
  domain   = var.domain
  type     = "CNAME"
  ttl      = 60
  name     = "www"
  value    = "@"
}

resource "digitalocean_certificate" "cert" {
  depends_on = [digitalocean_kubernetes_cluster.weerwijzer_cluster, digitalocean_domain.top_level_domains]
  name    = "cert-weerwijzer"
  type    = "lets_encrypt"
  domains = var.top_level_domains
}

resource "kubernetes_service" "weerwijzer_app_service" {
  depends_on = [ digitalocean_certificate.cert, kubernetes_deployment.weerwijzer_app]
  metadata {
    name = "weerwijzer-app-service"
    annotations = {
      "service.beta.kubernetes.io/do-loadbalancer-certificate-id" = digitalocean_certificate.cert.uuid
    }
  }
  spec {
    selector = {
      app = "weerwijzer-app"
    }
    port {
      port        = 443
      target_port = 8080
    }
    type = "LoadBalancer"
  }
}

resource "helm_release" "kube_prometheus_stack" {
  depends_on = [kubernetes_deployment.weerwijzer_app]
  name       = "kube-prometheus-stack"
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "kube-prometheus-stack"

  set {
    name  = "grafana.enabled"
    value = "true"
  }
}

resource "kubernetes_service" "prometheus_lb" {
  depends_on = [ helm_release.kube_prometheus_stack ]
  metadata {
    name = "prometheus-grafana-lb"
  }
  spec {
    selector = {
      app = helm_release.kube_prometheus_stack.metadata.0.name
    }
    port {
      port        = 80
      target_port = 3000
    }
    type = "LoadBalancer"
  }
}


# resource "grafana_folder" "test" {
#   title = "My Folder"
#   uid   = "my-folder-uid"
# }

# resource "grafana_dashboard" "test" {
#   folder = grafana_folder.test.uid
#   config_json = jsonencode({
#     "title" : "My Dashboard",
#     "uid" : "my-dashboard-uid"
#   })
# }
