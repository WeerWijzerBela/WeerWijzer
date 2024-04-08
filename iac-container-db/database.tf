resource "digitalocean_database_cluster" "db-cluster" {
  name       = "mysql-cluster"
  engine     = "mysql"
  version    = "8"
  size       = "db-s-1vcpu-1gb"
  region     = "ams3"
  node_count = 1
  private_network_uuid = digitalocean_vpc.db-network.id
}

resource "digitalocean_database_db" "weerwijzer-db" {
  depends_on = [digitalocean_database_cluster.db-cluster]
  cluster_id = digitalocean_database_cluster.db-cluster.id
  name       = "weerwijzer-db"
}

resource "digitalocean_vpc" "db-network" {
  name     = "private-network"
  region   = "ams3"
  #ip_range = "10.110.16.0/20"
}

