resource "kubernetes_deployment" "frontend" {
  metadata {
    name      = "frontend"
    namespace = kubernetes_namespace.main.metadata.0.name
    labels = {
      app = "frontend"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "frontend"
      }
    }

    template {
      metadata {
        labels = {
          app = "frontend"
        }
      }

      spec {
        container {
          name              = "frontend"
          image             = "zeebonk/wedding:frontend"
          image_pull_policy = "Always"
        }
        image_pull_secrets {
          name = "private-docker"
        }
      }
    }
  }
}

resource "kubernetes_service" "frontend" {
  metadata {
    name      = "frontend"
    namespace = kubernetes_namespace.main.metadata.0.name
  }
  spec {
    selector = {
      app = kubernetes_deployment.frontend.metadata.0.labels.app
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

resource "kubernetes_ingress" "frontend" {
  metadata {
    name      = "frontend"
    namespace = kubernetes_namespace.main.metadata.0.name
    annotations = {
      "kubernetes.io/ingress.class" = "traefik"
    }
  }

  spec {
    rule {
      host = digitalocean_record.frontend.domain
      http {
        path {
          path = "/"
          backend {
            service_name = kubernetes_service.frontend.metadata.0.name
            service_port = 80
          }
        }
      }
    }
  }
}

resource "digitalocean_record" "frontend" {
  domain = digitalocean_domain.main.name
  type   = "A"
  name   = "@"
  ttl    = 60
  value  = data.kubernetes_service.traefik_ingress.load_balancer_ingress.0.ip
}

output "frontend_domain" {
  value = digitalocean_record.frontend.domain
}
