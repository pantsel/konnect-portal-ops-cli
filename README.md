# Konnect Portal Ops Examples

This repository contains examples of how to use the Konnect Portal Ops API.

## Setup

1. Navigate to the `python` folder.
2. Copy the `.env.example` file to `.env` and fill in the required values:

    ```bash
    cp .env.example .env
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

To display the help message for the CLI tool, run:

```bash
python3 main.py --help
```

The usage information is as follows:

```
usage: main.py [-h] --oas-spec OAS_SPEC --konnect-portal-name KONNECT_PORTAL_NAME [--konnect-token KONNECT_TOKEN] [--konnect-url KONNECT_URL] [--deprecate] [--unpublish]

Konnect Dev Portal Ops CLI

options:
  -h, --help            show this help message and exit
  --oas-spec OAS_SPEC   Path to the OAS spec file
  --konnect-portal-name KONNECT_PORTAL_NAME
                        The name of the Konnect portal to perform operations on
  --konnect-token KONNECT_TOKEN
                        The Konnect spat or kpat token
  --konnect-url KONNECT_URL
                        The Konnect API server URL
  --deprecate           Deprecate the API product version
  --unpublish           Unpublish the API product version
```

### Publish Spec to a Portal

To publish an API product and its related associations to the specified portal, run the following command. The API product and version information will be extracted from the OAS spec file, and the specified spec will be attached to the API product version, which will then be published on the specified portal.

```bash
python3 main.py --oas-spec=../oasv1.yaml --konnect-portal-name=dev_portal
```

### Publish a New Version of an Existing API

To publish a new version of an existing API product to the specified portal, ensure that the OAS spec file has the same `info.title` as the existing API product on the portal and a different `info.version`. If these conditions are not met, a new API product and its related associations will be created and published on the specified portal.

```bash
# Dev portal
python3 main.py --oas-spec=../oasv2.yaml --konnect-portal-name=dev_portal
```

### Deprecate an API Product Version on a Portal

To deprecate the specified API product version on the specified portal, run the following command:

```bash
# Deprecate on Dev portal
python3 main.py --oas-spec=../oasv1.yaml --konnect-portal-name=dev_portal --deprecate
```

### Unpublish an API Product Version from a Portal

To unpublish the specified API product version from the specified portal, run the following command:

```bash
# Unpublish on Dev portal
python3 main.py --oas-spec=../oasv1.yaml --konnect-portal-name=dev_portal --unpublish
```
