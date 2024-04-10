resource "digitalocean_database_cluster" "db-cluster" {
  name       = "mysql-cluster-iac"
  engine     = "mysql"
  version    = "11"
  size       = "db-s-1vcpu-1gb"
  region     = "ams3"
  node_count = 1
}

resource "digitalocean_database_db" "database-mysql" {
  depends_on = [digitalocean_database_cluster.db-cluster]
  cluster_id = digitalocean_database_cluster.db-cluster.id
  name       = "database-weerwijzer"
}

output "database_user" {
  value = digitalocean_database_cluster.db-cluster.password
}

