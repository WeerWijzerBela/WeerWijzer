variable "do_token" {
  type = string
  default = "dop_v1_54768fea7051d1b3bcaa29e659330cf6a44eedc269130bc4057b45d218dcec85"
}

variable "cluster_name" {
  type = string
}

variable "cluster_id" {
  type = string
}

variable "write_kubeconfig" {
  type        = bool
  default     = false
}