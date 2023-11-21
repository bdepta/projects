# --- template/main.tf ---

module "image" {
  source   = "../../../terraform-modules/docker/image"
  for_each = local.deployment
  image    = each.value.image
}


module "container" {
  source       = "../../../terraform-modules/docker/container"
  for_each     = local.deployment
  name         = join("_", [each.key, "container"])
  image        = module.image[each.key].image_out
  hostname     = each.key
  network_mode = each.value.network_mode
  command      = each.value.command
  ports        = each.value.ports
}






