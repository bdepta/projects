<!-- BEGIN_TF_DOCS -->
## Requirements

No requirements.

## Providers

| Name | Version |
|------|---------|
| <a name="provider_docker"></a> [docker](#provider\_docker) | n/a |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [docker_container.container](https://registry.terraform.io/providers/kreuzwerker/docker/latest/docs/resources/container) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_command"></a> [command](#input\_command) | Override the default command | `list(string)` | `null` | no |
| <a name="input_devices"></a> [devices](#input\_devices) | Device mappings | <pre>map(object({<br>    container_path = string<br>    permissions    = string<br>  }))</pre> | `{}` | no |
| <a name="input_host_paths"></a> [host\_paths](#input\_host\_paths) | Mount host paths | <pre>map(object({<br>    container_path = string<br>    read_only      = bool<br>  }))</pre> | `{}` | no |
| <a name="input_hostname"></a> [hostname](#input\_hostname) | Set docker hostname | `string` | `null` | no |
| <a name="input_image"></a> [image](#input\_image) | Name of docker image to pull. | `string` | `null` | no |
| <a name="input_name"></a> [name](#input\_name) | Custom container name | `string` | `null` | no |
| <a name="input_named_volumes"></a> [named\_volumes](#input\_named\_volumes) | Mount named volumes | <pre>map(object({<br>    container_path = string<br>    read_only      = bool<br>    create         = bool<br>  }))</pre> | `{}` | no |
| <a name="input_network_mode"></a> [network\_mode](#input\_network\_mode) | Specify a custom network mode | `string` | `"bridge"` | no |
| <a name="input_ports"></a> [ports](#input\_ports) | Expose ports | <pre>list(object({<br>    internal = number<br>    external = number<br>    protocol = string<br>  }))</pre> | `null` | no |
| <a name="input_restart_policy"></a> [restart\_policy](#input\_restart\_policy) | Restart policy. Default: no | `string` | `"no"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_container_name"></a> [container\_name](#output\_container\_name) | The name of the container |
<!-- END_TF_DOCS -->