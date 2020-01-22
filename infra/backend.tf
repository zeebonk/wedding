variable reset_code {}
variable next_stage_code {}

resource "kubernetes_deployment" "backend" {
  metadata {
    name      = "backend"
    namespace = kubernetes_namespace.main.metadata.0.name
    labels = {
      app = "backend"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "backend"
      }
    }

    template {
      metadata {
        labels = {
          app = "backend"
        }
      }

      spec {
        container {
          name              = "backend"
          image             = "zeebonk/wedding:backend"
          image_pull_policy = "Always"

          env {
            name  = "PG_USERNAME"
            value = digitalocean_database_cluster.main.user
          }
          env {
            name  = "PG_PASSWORD"
            value = digitalocean_database_cluster.main.password
          }
          env {
            name  = "PG_DATABASE"
            value = digitalocean_database_cluster.main.database
          }
          env {
            name  = "PG_HOST"
            value = digitalocean_database_cluster.main.private_host
          }
          env {
            name  = "PG_PORT"
            value = digitalocean_database_cluster.main.port
          }
          env {
            name  = "PG_CADATA"
            value = file("pg-certificate.crt")
          }
          env {
            name  = "RESET_CODE"
            value = var.reset_code
          }
          env {
            name  = "NEXT_STAGE_CODE"
            value = var.next_stage_code
          }
        }
        image_pull_secrets {
          name = "private-docker"
        }
      }
    }
  }
}

resource "kubernetes_service" "backend" {
  metadata {
    name      = "backend"
    namespace = kubernetes_namespace.main.metadata.0.name
  }
  spec {
    selector = {
      app = kubernetes_deployment.backend.metadata.0.labels.app
    }
    port {
      port        = 8000
      target_port = 8000
    }
  }

  lifecycle {
    ignore_changes = [
      metadata.0.annotations,
    ]
  }
}

resource "kubernetes_ingress" "backend" {
  metadata {
    name      = "backend"
    namespace = kubernetes_namespace.main.metadata.0.name
    annotations = {
      "kubernetes.io/ingress.class" = "traefik"
    }
  }

  spec {
    rule {
      host = digitalocean_record.backend.fqdn
      http {
        path {
          path = "/"
          backend {
            service_name = kubernetes_service.backend.metadata.0.name
            service_port = 8000
          }
        }
      }
    }
  }
}

resource "digitalocean_record" "backend" {
  domain = digitalocean_domain.main.name
  type   = "A"
  name   = "ws"
  ttl    = 60
  value  = data.kubernetes_service.traefik_ingress.load_balancer_ingress.0.ip
}

output "backend_domain" {
  value = digitalocean_record.backend.fqdn
}
