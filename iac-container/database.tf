resource "digitalocean_database_cluster" "db-cluster" {
  name       = "mysql-cluster-iac"
  engine     = "mysql"
  version    = "8"
  size       = "db-s-1vcpu-1gb"
  region     = "ams3"
  node_count = 1
}

resource "digitalocean_database_db" "database-mysql" {
  depends_on = [digitalocean_database_cluster.db-cluster]
  cluster_id = digitalocean_database_cluster.db-cluster.id
  name       = "database-weerwijzer"
}


#data "github_repository" "repo" {
#  full_name = "WeerWijzerBela/WeerWijzer"
#}
resource "github_actions_secret" "example_secret" {
  depends_on = [digitalocean_database_cluster.db-cluster]
  repository       = "WeerWijzerBela/WeerWijzer"
  secret_name      = "DB_USER_2"
  plaintext_value  = digitalocean_database_cluster.db-cluster.user
}

resource "github_actions_secret" "example_secret" {
  depends_on = [digitalocean_database_cluster.db-cluster]
  repository       = "example_repository"
  secret_name      = "DB_PASSWORD_2"
  encrypted_value  = digitalocean_database_cluster.db-cluster.password
}


