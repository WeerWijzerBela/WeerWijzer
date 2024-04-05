output "weerwijzer_app_service_ip" {
  value = kubernetes_service.weerwijzer_app_service.status.0.load_balancer.0.ingress.0.ip

}