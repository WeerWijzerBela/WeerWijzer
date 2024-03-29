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

resource "kubernetes_deployment" "weerwijzer" {
	metadata {
		name = "weerwijzer"
		labels = {
			test = "weerwijzer"
		}
		namespace = "weerwijzer"
	}
	spec {
		replicas = 5

		selector {
			match_labels = {
				test = "weerwijzer"
			}
		}

		template {
			metadata {
				labels = {
					test = "weerwijzer"
				}
			}

			spec {
				container {
					image = "registry.digitalocean.com/container-weerwijzer/weerwijzer-app:latest"
					image_pull_policy = "IfNotPresent"
					name = "weerwijzer"
					port {
                        container_port = 80
                    }
				}
			}

		}
	}
}


