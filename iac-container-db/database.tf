
#resource "digitalocean_database_db" "weerwijzer-db" {
#  cluster_id = digitalocean_database_cluster.postgres-example.id
#  name       = "foobar"
#}
#
#resource "digitalocean_database_cluster" "db-cluster" {
#  name       = "example-postgres-cluster"
#  engine     = "mysql"
#  version    = "11"
#  size       = "db-s-1vcpu-1gb"
#  region     = "nyc1"
#  node_count = 1
#}