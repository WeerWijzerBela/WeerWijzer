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


data "github_repository" "repo" {
  depends_on = [digitalocean_database_cluster.db-cluster]
  full_name = "WeerWijzerBela/WeerWijzer"
}

resource "github_actions_secret" "db_name" {
  repository       = data.github_repository.repo.name
  secret_name      = "DB_NAME_2"
  plaintext_value  = digitalocean_database_cluster.db-cluster.name
}

resource "github_actions_secret" "db_password" {
  repository       = data.github_repository.repo.name
  secret_name      = "DB_PASSWORD_2"
  encrypted_value  = digitalocean_database_cluster.db-cluster.password
}

resource "github_actions_secret" "db_host" {
  repository       = data.github_repository.repo.name
  secret_name      = "DB_HOST_2"
  plaintext_value  = digitalocean_database_cluster.db-cluster.host
}
resource "github_actions_secret" "db_port" {
  repository       = data.github_repository.repo.name
  secret_name      = "DB_PORT_2"
  plaintext_value  = digitalocean_database_cluster.db-cluster.port
}
resource "github_actions_secret" "db_user" {
  repository       = data.github_repository.repo.name
  secret_name      = "DB_USER_2"
  plaintext_value  = digitalocean_database_cluster.db-cluster.user
}



