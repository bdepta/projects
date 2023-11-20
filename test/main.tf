module "image" {
  source   = "./image"
  for_each = var.deployment
  image_in = each.value.image
}


module "container" {
  source            = "./container"
  for_each = var.deployment
  name_in           = join("-", [each.key, terraform.workspace])
  image_in          = module.image[each.key].image_out
  int_port_in       = each.value.ports.*.internal
  ext_port_in       = each.value.ports.*.external
  container_path_in = "/data"
}






