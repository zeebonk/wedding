resource "digitalocean_kubernetes_cluster" "main" {
  name    = "wedding"
  region  = local.region
  version = "1.16.2-do.1"

  node_pool {
    name       = "wedding-worker-pool"
    size       = "s-2vcpu-4gb"
    node_count = 1
  }
}

resource "kubernetes_namespace" "main" {
  metadata {
    name = "wedding"
  }
}

provider "kubernetes" {
  host  = digitalocean_kubernetes_cluster.main.endpoint
  token = digitalocean_kubernetes_cluster.main.kube_config[0].token
  cluster_ca_certificate = base64decode(
    digitalocean_kubernetes_cluster.main.kube_config[0].cluster_ca_certificate
  )
}

provider "helm" {
  service_account = "tiller"
  kubernetes {
    host  = digitalocean_kubernetes_cluster.main.endpoint
    token = digitalocean_kubernetes_cluster.main.kube_config[0].token
    cluster_ca_certificate = base64decode(
      digitalocean_kubernetes_cluster.main.kube_config[0].cluster_ca_certificate
    )
  }
}

resource "kubernetes_service_account" "tiller" {
  metadata {
    name      = "tiller"
    namespace = "kube-system"
  }
}

resource "kubernetes_cluster_role_binding" "tiller-cluster-admin" {
  metadata {
    name = "tiller-cluster-admin"
  }
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = "cluster-admin"
  }
  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account.tiller.metadata.0.name
    namespace = "kube-system"
  }
}

data "helm_repository" "stable" {
  name = "stable"
  url  = "https://kubernetes-charts.storage.googleapis.com"
}

resource "helm_release" "traefik_ingress" {
  name       = "traefik-ingress"
  chart      = "stable/traefik"
  namespace  = "kube-system"
  repository = data.helm_repository.stable.metadata[0].name
  version    = "1.85.0"

  set {
    name  = "rbac.enabled"
    value = "true"
  }
  set {
    name  = "debug.enabled"
    value = "true"
  }
  set {
    name  = "traefikLogFormat"
    value = "common"
  }
  set {
    name  = "accessLogs.enabled"
    value = "true"
  }
}

data "kubernetes_service" "traefik_ingress" {
  metadata {
    name      = "traefik-ingress"
    namespace = "kube-system"
  }
}
