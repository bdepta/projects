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
| [docker_image.container_image](https://registry.terraform.io/providers/kreuzwerker/docker/latest/docs/resources/image) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_image"></a> [image](#input\_image) | Name of docker image to pull. | `string` | `null` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_image_out"></a> [image\_out](#output\_image\_out) | n/a |
<!-- END_TF_DOCS -->