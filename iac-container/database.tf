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

resource "github_actions_organization_secret" "database_user_2" {
  depends_on = [data.github_repository.repo]
  secret_name             = "DB_USER_2"
  visibility              = "all"
  plaintext_value         = digitalocean_database_cluster.db-cluster.user
  # selected_repository_ids = [data.github_repository.repo.repo_id]
}

resource "github_actions_organization_secret" "database_password_2" {
  depends_on = [data.github_repository.repo]
  secret_name             = "DB_PASSWORD_2"
  visibility              = "all"
  plaintext_value         = digitalocean_database_cluster.db-cluster.password
  # selected_repository_ids = [data.github_repository.repo.repo_id]
}
resource "github_repository_environment" "repo_environment" {
  depends_on = [data.github_repository.repo]
  repository       = data.github_repository.repo.name
  environment      = "example_environment"
}

resource "github_actions_environment_secret" "test_secret" {
  depends_on = [data.github_repository.repo]
  repository       = data.github_repository.repo.name
  environment      = github_repository_environment.repo_environment.environment
  secret_name      = "test_secret_name"
  plaintext_value  = "%s"
}