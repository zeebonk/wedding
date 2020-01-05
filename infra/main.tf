provider "digitalocean" {}

variable domain {}

locals {
  region = "ams3"
}

resource "digitalocean_domain" "main" {
  name = var.domain
}
