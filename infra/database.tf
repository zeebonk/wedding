variable home_ip {}

resource "digitalocean_database_cluster" "main" {
  name       = "wedding"
  engine     = "pg"
  version    = "11"
  size       = "db-s-1vcpu-1gb"
  region     = local.region
  node_count = 1
}

resource "digitalocean_database_firewall" "main" {
  cluster_id = digitalocean_database_cluster.main.id

  rule {
    type  = "k8s"
    value = digitalocean_kubernetes_cluster.main.id
  }

  rule {
    type  = "ip_addr"
    value = var.home_ip
  }
}
