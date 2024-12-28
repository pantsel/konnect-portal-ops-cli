# Konnect Dev Portal Ops CLI <!-- omit in toc -->

A rather opinionated CLI tool for managing API products on **Konnect Developer Portals**.

This tool performs operations such as publishing, deprecating, unpublishing, or deleting API products and their versions based on state files.

Ensure that the required Konnect Developer Portals are set up before using this tool.

> **Note:** The CLI is under active development. Some features may not be fully supported yet. Use responsibly and report any issues.

## Table of Contents <!-- omit in toc -->
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Available Commands](#available-commands)
    - [`sync`](#sync)
    - [`delete`](#delete)
    - [`explain`](#explain)
  - [Common Arguments](#common-arguments)
  - [Advanced Examples](#advanced-examples)
    - [Unpublish API Product Versions](#unpublish-api-product-versions)
    - [Deprecate API Product Versions](#deprecate-api-product-versions)
    - [Link Gateway Services to API Product Versions](#link-gateway-services-to-api-product-versions)
    - [Manage API Products Documentation](#manage-api-products-documentation)
- [Full State File Explanation](#full-state-file-explanation)
  - [Version](#version)
  - [Info](#info)
  - [Documents](#documents)
  - [Portals](#portals)
  - [Versions](#versions)
- [Logging](#logging)
- [Local Development](#local-development)
  - [Requirements](#requirements)
- [Testing](#testing)

## Features

- **Publish or update API Products and Versions** on a Konnect Dev Portal.
- Link **Gateway Services** to **API Product Versions**.
- Manage **API Product Documents**.
- **Deprecate or unpublish API versions**.
- **Delete API products** and their associations.
- Supports **non-interactive modes** for automation.

## Installation

1. Install the CLI using `pip`:

    ```shell
    pip install kptl
    ```

2. (Optional) Create a `yaml` config file to set the CLI configuration variables:

    ```yaml
    # $HOME/.kptl.config.yaml
    konnect_url: https://us.api.konghq.com
    konnect_token: <your-konnect-token>
    http_proxy: http://proxy.example.com:8080 # Optional
    https_proxy: https://proxy.example.com:8080 # Optional
    ```

## Usage

```shell
kptl [command] [options]
```

### Available Commands

#### `sync`

Synchronize the predefined API Product state with Konnect Developer Portals.

Example state file:

```yaml
# httpbin_state.yaml
_version: 1.0.0
info:
   name: HTTPBin API
   description: A simple API Product for requests to httpbin
portals:
   - name: dev_portal
   - name: prod_portal
versions:
   - name: "1.0.0"
      spec: examples/api-specs/v1/httpbin.yaml
      portals:
         - name: dev_portal
         - name: prod_portal
   - name: "2.0.0"
      spec: examples/api-specs/v2/httpbin.yaml
      portals:
         - name: dev_portal
         - name: prod_portal
```

To sync the API Product state with Konnect, run:

```shell
kptl sync httpbin_state.yaml --config .config.yaml
```

This command will:
1. Ensure the API Product is created on Konnect.
2. Publish the API Product to the specified portals.
3. Create the API Product versions on Konnect.
4. Upload the defined API specifications to the respective API Product versions.
5. Publish the API Product versions to the specified portals.

```mermaid
graph LR
      A[API Product State File] --> B[Create API Product]
      B --> C[Publish API Product]
      C --> D[Create API Product Versions]
      D --> E[Upload API Specifications]
      E --> F[Publish API Product Versions]
```

#### `delete`

Delete the API Product and its associations from Konnect.

```shell
kptl delete product_name_or_id --config .config.yaml
```

To skip the interactive confirmation prompt, use the `--yes` flag:

```shell
kptl delete product_name_or_id --config .config.yaml --yes
```

#### `explain`

Explain the API Product state file and the operations that will be performed on Konnect.

```shell
kptl explain httpbin_state.yaml
```

### Common Arguments

| Option            | Required                         | Description                                                                |
| ----------------- | -------------------------------- | -------------------------------------------------------------------------- |
| `--konnect-token` | **Yes** (if config file not set) | The Konnect token to use for authentication.                               |
| `--konnect-url`   | **Yes** (if config file not set) | The Konnect API server URL.                                                |
| `--config`        | No                               | Path to the CLI configuration file. Defaults to `$HOME/.kptl.config.yaml`. |
| `--http-proxy`    | No                               | HTTP proxy URL.                                                            |
| `--https-proxy`   | No                               | HTTPS proxy URL.                                                           |

### Advanced Examples

For a full state file example, see the [examples/products/httpbin/httpbin_state.yaml](examples/products/httpbin/httpbin_state.yaml) file.

#### Unpublish API Product Versions

To unpublish an API Product version from a portal, update the state file to set the `publish_status` to `unpublished` for the desired portal.

```yaml
# httpbin_state.yaml
...
versions:
   - name: "1.0.0"
      spec: examples/api-specs/v1/httpbin.yaml
      portals:
         - name: dev_portal
            config:
               publish_status: unpublished
...
```

Then run the sync command:

```shell
kptl sync httpbin_state.yaml --config .config.yaml
```

#### Deprecate API Product Versions

To deprecate an API Product version from a portal, update the state file to set `deprecated` to `true` for the desired portal.

```yaml
# httpbin_state.yaml
...
versions:
   - name: "1.0.0"
      spec: examples/api-specs/v1/httpbin.yaml
      portals:
         - name: dev_portal
            config:
               deprecated: true
...
```

Then run the sync command:

```shell
kptl sync httpbin_state.yaml --config .config.yaml
```

#### Link Gateway Services to API Product Versions

To link a Gateway Service to an API Product version, update the state file to include the `gateway_service` section with the appropriate `id` and `control_plane_id`.

```yaml
# httpbin_state.yaml
...
versions:
   - name: "1.0.0"
      spec: examples/api-specs/v1/httpbin.yaml
      gateway_service:
         id: <gateway-service-id>
         control_plane_id: <control-plane-id>
...
```

Then run the sync command:

```shell
kptl sync httpbin_state.yaml --config .config.yaml
```

#### Manage API Products Documentation

To manage API Product documents, ensure all related documents are present in a directory. The ordering and inheritance of documents are based on file name prefixes (e.g., `1_, 1.1_, 1.2_, 2_, 3_, 3.1_`). By default, all documents get published. To unpublish a document, add the `__unpublished` tag at the end of the file name. Existing API Product documents not present in the documents folder will be deleted.

For an example documents folder structure, see the [examples/products/httpbin/docs](examples/products/httpbin/docs) directory.

To sync the API Product documents, update the state file to include the `documents` section with the `sync` flag set to `true` and the `dir` pointing to the documents directory.

```yaml
# httpbin_state.yaml
...
info: ...
documents:
   sync: true
   dir: examples/products/httpbin/docs
...
```

Then run the sync command:

```shell
kptl sync httpbin_state.yaml --config .config.yaml
```

## Full State File Explanation

The example state file at [examples/products/httpbin/httpbin_state.yaml](examples/products/httpbin/httpbin_state.yaml) defines the configuration for the HTTPBin API product.

### Version

```yaml
_version: 1.0.0
```

Specifies the version of the state file format.

### Info

```yaml
info:
   name: HTTPBin API
   description: A simple API Product for requests to /httpbin
```

Contains metadata about the API product, including its name and description.

### Documents

```yaml
documents:
   sync: true
   dir: examples/products/httpbin/docs
```

Defines the synchronization settings and directory for the API documentation.

### Portals

```yaml
portals:
   - name: dev_portal
      config:
         publish_status: published
   - name: prod_portal
      id: <prod_portal_id>
      config:
         publish_status: unpublished
```

Lists the portals where the API product will be published, along with their publication status. If the portal `id` is specified, it will take precedence over the portal name for operations. The `config.publish_status` is optional and defaults to `published`.

### Versions

```yaml
versions:
   - name: "1.0.0"
      spec: examples/api-specs/v1/httpbin.yaml
      gateway_service:
         id: null
         control_plane_id: null
      portals:
         - name: dev_portal
            config:
               deprecated: true
               publish_status: published
               auth_strategy_ids: []
               application_registration:
                  enabled: false
                  auto_approve: false
         - name: prod_portal
            config:
               deprecated: true
               publish_status: published
               auth_strategy_ids: []
               application_registration:
                  enabled: false
                  auto_approve: false
   - name: "2.0.0"
      spec: examples/api-specs/v2/httpbin.yaml
      gateway_service:
         id: null
         control_plane_id: null
      portals:
         - name: dev_portal
            config:
               deprecated: false
               publish_status: published
               auth_strategy_ids: []
               application_registration:
                  enabled: false
                  auto_approve: false
         - name: prod_portal
            config:
               deprecated: false
               publish_status: published
               auth_strategy_ids: []
               application_registration:
                  enabled: false
                  auto_approve: false
```

Defines the different versions of the API product, including their specifications, gateway service details, and portal configurations. Each version can have different settings for deprecation, publication status, authentication strategies, and application registration.

- The `version.name` field is optional and defaults to the version specified in the OAS spec file.
- The `gateway_service` section is optional and can be used to link a Gateway Service to the API Product version.
- The `portals` section lists the portals where the API Product version will be published, along with their configurations.
- The `portal.config` is optional:
   - `deprecated`: defaults to `false`.
   - `publish_status`: defaults to `published`.
   - `auth_strategy_ids`: defaults to an empty list.
   - `application_registration.enabled`: defaults to `false`.
   - `application_registration.auto_approve`: defaults to `false`.

## Logging

The CLI uses the `logging` module to log messages to the console. The default log level is set to `INFO`.

To change the log level, set the `LOG_LEVEL` environment variable to one of the following values: `DEBUG`, `INFO`, `WARNING`, or `ERROR`.

## Local Development

### Requirements

- Python 3+
- `PyYaml`: For parsing YAML-based files.
- `requests`: For making HTTP requests to the Konnect API.

1. Clone the repository:

    ```shell
    git clone https://github.com/pantsel/konnect-portal-ops-cli
    ```

2. Install the dependencies:

    ```shell
    make deps
    ```

3. Run the CLI directly:

    ```shell
    PYTHONPATH=src python src/kptl/main.py [command] [options]
    ```

## Testing

To run the tests, use the following command from the root directory:

```shell
make test
```