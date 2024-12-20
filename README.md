# Konnect Portal Ops Examples

This repository contains examples of how to use the Konnect Portal Ops API.

## Setup

In the `python` folder, copy the `.env.example` file to `.env` and fill in the required values.

```bash
cp .env.example .env
```

Install required packages:

```bash
pip install -r requirements.txt
```

## Usage

```bash
$ python3 main.py --help

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

Publish oas.yaml to Konnect Developer Portals:

```bash
# Dev portal
$ python3 main.py --oas_spec=../oasv1.yaml --konnect-portal-name=dev_portal

# Prod portal
$ python3 main.py --oas_spec=../oasv1.yaml --konnect-portal-name=prod_portal
```

Publish a new version of an existing API (oas2.yaml) to Konnect Portals:

```bash
# Dev portal
$ python3 main.py --oas_spec=../oasv2.yaml --konnect-portal-name=dev_portal

# Prod portal
$ python3 main.py --oas_spec=../oasv2.yaml --konnect-portal-name=prod_portal
```

Deprecating an API product version on a portal:

```bash

# Deprecate on Dev portal
$ python3 main.py --oas_spec=../oasv1.yaml --konnect-portal-name=dev_portal --deprecate
```

Unpublishing an API product version from a portal:

```bash

# Unpublish on Dev portal
$ python3 main.py --oas_spec=../oasv1.yaml --konnect-portal-name=dev_portal --unpublish
```
