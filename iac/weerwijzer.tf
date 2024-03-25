resource "kubernetes_namespace" "weerwijzerApp" {
	metadata {
		name = "weerwijzer"
	}
}

resource "kubernetes_persistent_volume_claim" "postgres_pvc" {
	metadata {
		name = "postgres-pvc"
		namespace = "weerwijzer"
	}
	spec {
		access_modes = ["ReadWriteOnce"]
		resources {
			requests = {
				storage = "1Gi"  # Adjust the storage size as needed
			}
		}
	}
}

resource "kubernetes_deployment" "weerwijzer" {
	metadata {
		name = "weerwijzer-app"
		labels = {
			test = "WeerWijzerApp"
		}
		namespace = "weerwijzer"
	}


	spec {
		replicas = 5

		selector {
			match_labels = {
				test = "WeerWijzerApp"
			}
		}

		template {
			metadata {
				labels = {
					test = "WeerWijzerApp"
				}
			}

			spec {
				container {
					image = "jokp/weerwijzer"
					image_pull_policy = "IfNotPresent"
					name = "weerwijzer"
					env {
						name  = "DATABASE_URL"
						value = "postgresql://your_username:your_password@postgres:5432/your_database_name"
					}
				}
			}

		}
	}
}

# Define the PostgreSQL Deployment and Service
resource "kubernetes_deployment" "postgres" {
	metadata {
		name = "postgres"
		labels = {
			app = "postgres"
		}
		namespace = "weerwijzer"
	}

	spec {
		replicas = 2
		selector {
			match_labels = {
				app = "postgres"
			}
		}
		template {
			metadata {
				labels = {
					app = "postgres"
				}
			}
			spec {
				container {
					name  = "postgres"
					image = "postgres:latest"
					env {
						name  = "POSTGRES_USER"
						value = "your_username"
					}
					env {
						name  = "POSTGRES_PASSWORD"
						value = "your_password"
					}
					env {
						name  = "POSTGRES_DB"
						value = "your_database_name"
					}
				}
				volume {
					name = "postgres-data"
					persistent_volume_claim {
						claim_name = kubernetes_persistent_volume_claim.postgres_pvc.metadata[0].name
					}
				}
			}
		}
	}
}

resource "kubernetes_service" "postgres" {
	metadata {
		name = "postgres"
		namespace = "kroket"
	}

	spec {
		selector = {
			app = "postgres"
		}
		port {
			port        = 5432
			target_port = 5432
		}
	}
}

resource "kubernetes_service" "buurman" {
	metadata {
		name = "fastapi"
		namespace = "kroket"
	}

	spec {
		selector = {
			test = "FastApiExample"
		}

		port {
			port = 80
			target_port = 8000

		}
		type = "LoadBalancer"
	}

}
