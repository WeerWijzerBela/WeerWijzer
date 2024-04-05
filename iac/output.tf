output "weerwijzer_app_service_ip" {
  value = kubernetes_service.weerwijzer_app_service.load_balancer_ip
}