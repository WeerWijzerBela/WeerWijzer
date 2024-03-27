resource "kubernetes_deployment" "weerwijzer_api" {
  metadata {
    name = "weerwijzer-api"
  }

  spec {
    selector {
      match_labels = {
        app = "weerwijzer-api"
      }
    }

    template {
      metadata {
        labels = {
          app = "weerwijzer-api"
        }
      }

      spec {
        container {
          image = "registry.digitalocean.com/container-weerwijzer/weerwijzer-api:latest"
          name  = "weerwijzer-api"
          # Add other container settings as needed
        }
      }
    }
  }
}
