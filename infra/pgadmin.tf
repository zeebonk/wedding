variable pgadmin_password {}

resource "kubernetes_deployment" "pgadmin" {
  metadata {
    name      = "pgadmin"
    namespace = kubernetes_namespace.main.metadata.0.name
    labels = {
      app = "pgadmin"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "pgadmin"
      }
    }

    template {
      metadata {
        labels = {
          app = "pgadmin"
        }
      }

      spec {
        container {
          image = "dpage/pgadmin4:latest"
          name  = "pgadmin"

          env {
            name  = "PGADMIN_DEFAULT_EMAIL"
            value = "admin@${digitalocean_domain.main.name}"
          }

          env {
            name  = "PGADMIN_DEFAULT_PASSWORD"
            value = var.pgadmin_password
          }

          env {
            name  = "PGADMIN_PORT"
            value = "5050"
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "pgadmin" {
  metadata {
    name      = "pgadmin"
    namespace = kubernetes_namespace.main.metadata.0.name
  }
  spec {
    selector = {
      app = kubernetes_deployment.pgadmin.metadata.0.labels.app
    }
    port {
      port        = 80
      target_port = 80
    }
  }

  lifecycle {
    ignore_changes = [
      metadata.0.annotations,
    ]
  }
}

resource "kubernetes_ingress" "pgadmin" {
  metadata {
    name      = "pgadmin"
    namespace = kubernetes_namespace.main.metadata.0.name
    annotations = {
      "kubernetes.io/ingress.class" = "traefik"
    }
  }

  spec {
    rule {
      host = digitalocean_record.pgadmin.fqdn
      http {
        path {
          path = "/"
          backend {
            service_name = kubernetes_service.pgadmin.metadata.0.name
            service_port = 80
          }
        }
      }
    }
  }
}

resource "digitalocean_record" "pgadmin" {
  domain = digitalocean_domain.main.name
  type   = "A"
  name   = "pgadmin"
  ttl    = 60
  value  = data.kubernetes_service.traefik_ingress.load_balancer_ingress.0.ip
}

output "pgadmin_domain" {
  value = digitalocean_record.pgadmin.fqdn
}
