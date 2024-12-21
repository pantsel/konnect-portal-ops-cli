# Konnect Dev Portal Ops CLI

This script is a command-line tool designed to perform various operations on **Konnect Dev Portals**, such as publishing, deprecating, unpublishing, or deleting API products and their versions based on OpenAPI Specification (OAS) files.

The script requires Konnect Developer Portals to be set up and pre-configured. It uses the Konnect APIs to interact with the portals and perform API Product related operations.

## Disclaimer

Heads up! This script is still a work in progress, so some features might not be fully supported yet. Feel free to give it a try, but please use it responsibly. If something doesn’t work as expected, let us know—or better yet, contribute!

## Features

- **Publish or update API products** on a Konnect Dev Portal.  
- **Deprecate or unpublish API versions**.  
- **Delete API products** and their associations.  
- Manage **API product documentation**.
- Supports **non-interactive modes** for automation.  

## Requirements

- Python 3+  
- Dependencies listed in [requirements.txt](#dependencies).  

## Installation

1. Clone this repository:  
   ```shell
      $ git clone https://github.com/pantsel/konnect-portal-ops-examples
      $ cd konnect-portal-ops-examples/python
   ```

2. Install dependencies:  
   ```shell
      $ pip install -r requirements.txt
   ```

3. (Optional) Create a `yaml` config file to set the configuration variables.  
   ```yaml
      # .config.yaml
      konnect_url: https://us.api.konghq.com
      konnect_token: <your-konnect-token>
   ```

## Usage

Run the script using the following command:  

```shell
$ python main.py [options]  
```

### Arguments

| Option                  | Required                                                | Description                                                          |
| ----------------------- | ------------------------------------------------------- | -------------------------------------------------------------------- |
| `--oas-spec`            | **Yes**                                                 | Path to the OAS spec file.                                           |
| `--docs`                | No                                                      | Path to the API product documents folder.                            |
| `--konnect-portal-name` | **Yes** (except for `--delete`)                         | Name of the Konnect portal to perform operations on.                 |
| `--konnect-token`       | **Yes** (except for `--config`)                         | The Konnect spat or kpat token.                                      |
| `--konnect-url`         | **Yes** (except for `--config`)                         | The Konnect API server URL.                                          |
| `--deprecate`           | No                                                      | Deprecate the API product version on the portal.                     |
| `--unpublish`           | No                                                      | Unpublish the API product version from the portal.                   |
| `--delete`              | No                                                      | Delete the API product and it's associations.                        |
| `--yes`                 | No                                                      | Skip confirmation prompts (useful for non-interactive environments). |
| `--config`              | **Yes** (except for `--konnect-token`, `--konnect-url`) | Path to the configuration file.                                      |

### Examples

#### Publish an API Product to a Portal

```bash
$ python main.py --config .config.yaml \
   --oas-spec ../examples/oasv1.yaml \
   --konnect-portal-name my-portal 
```
#### Publish a new version of the API Product to a Portal

```bash
python main.py --config .config.yaml \
   --oas-spec ../examples/oasv2.yaml \
   --konnect-portal-name my-portal
```

#### Deprecate an API Version on a Portal

```bash
python main.py --config .config.yaml \
   --oas-spec ../examples/oasv1.yaml \
   --konnect-portal-name my-portal --deprecate
```

#### Unpublish an API Version from a Portal

```bash
python main.py --config .config.yaml \
   --oas-spec ../examples/oasv1.yaml \
   --konnect-portal-name my-portal --unpublish
```

#### Managing API Products documentation

How it works:
- All related API Product documents must be present in a directory.
- All `.md` files in the directory are considered documentation files.
- The ordering of the documents on Konnect is based on the file names.
- By default, all documents get published. If you want to unpublish a document, add the `__unpublished` tag at the end of the file name.
- Existing API Product documents that are not present in the documents folder will be deleted.

For an example documents folder structure and use-cases, see the [examples/docs](examples/docs) directory.

```bash
python main.py --config .config.yaml \
   --oas-spec ../examples/oasv1.yaml \
   --docs ../examples/docs \
   --konnect-portal-name my-portal
```

#### Completely delete an API Product and its associations

```bash
python main.py --config .config.yaml \
   --oas-spec ../examples/oasv1.yaml --delete --yes
```

## CLI Configuration

The CLI supports the following variables for configuration in a `yaml` file:  

| Variable        | Description                            |
| --------------- | -------------------------------------- |
| `konnect_url`   | Konnect API server URL.                |
| `konnect_token` | Token for authenticating API requests. |

And the following environment variables:

| Variable    | Description                                                                     |
| ----------- | ------------------------------------------------------------------------------- |
| `LOG_LEVEL` | Logging verbosity level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). Default: `INFO`. |

## How It Works

1. **Parse OAS Spec**: The script reads the provided OpenAPI Specification (OAS) file and extracts essential API metadata such as title, version, and description.  
2. **Authentication**: The `KonnectApi` client is initialized using the provided token and Konnect URL.  
3. **Operations**:  
   - If the `--delete` flag is set, the script deletes the API product after confirmation.  
   - Otherwise, the API product is created or updated, its spec is uploaded, and it is published or deprecated based on the provided flags.  

## Logging

Logs are output to the console, and the verbosity is controlled by the `LOG_LEVEL` environment variable. Available levels are:  

- `DEBUG`: Detailed information for troubleshooting.  
- `INFO`: General operational messages (default).  
- `WARNING`: Non-critical issues.  
- `ERROR`: Critical errors that prevent execution.  

## Dependencies

The script requires the following Python libraries:  

- `PyYaml`: For parsing YAML-based files.  
- `requests`: For making HTTP requests to the Konnect API.

Install all dependencies using: `pip install -r requirements.txt` 

## Error Handling

The script includes robust error handling and will:  

- Log errors with a descriptive message.  
- Exit with a non-zero status code in case of failures.  