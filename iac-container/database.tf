resource "digitalocean_database_cluster" "db-cluster" {
  name       = "mysql-cluster-iac"
  engine     = "mysql"
  version    = "8"
  size       = "db-s-1vcpu-1gb"
  region     = "ams3"
  node_count = 1
}

data "github_repository" "repo" {
  depends_on = [digitalocean_database_cluster.db-cluster]
  full_name = "WeerWijzerBela/WeerWijzer"
}

resource "github_actions_secret" "db_name" {
  repository       = data.github_repository.repo.name
  secret_name      = "DB_NAME"
  plaintext_value  = "defaultdb"
}

resource "github_actions_secret" "db_password" {
  repository       = data.github_repository.repo.name
  secret_name      = "DB_PASSWORD"
  plaintext_value  = digitalocean_database_cluster.db-cluster.password
}

resource "github_actions_secret" "db_host" {
  repository       = data.github_repository.repo.name
  secret_name      = "DB_HOST"
  plaintext_value  = digitalocean_database_cluster.db-cluster.host
}
resource "github_actions_secret" "db_port" {
  repository       = data.github_repository.repo.name
  secret_name      = "DB_PORT"
  plaintext_value  = digitalocean_database_cluster.db-cluster.port
}
resource "github_actions_secret" "db_user" {
  repository       = data.github_repository.repo.name
  secret_name      = "DB_USER"
  plaintext_value  = digitalocean_database_cluster.db-cluster.user
}



