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

Publish oas.yaml to Konnect Developer Portals:

```bash
# Dev portal
python3 main.py --oas_spec=../oasv1.yaml --konnect-portal-name=dev_portal

# Prod portal
python3 main.py --oas_spec=../oasv1.yaml --konnect-portal-name=prod_portal
```

Publish a new version of an existing API (oas2.yaml) to Konnect Portals:

```bash
# Dev portal
python3 main.py --oas_spec=../oasv2.yaml --konnect-portal-name=dev_portal

# Prod portal
python3 main.py --oas_spec=../oasv2.yaml --konnect-portal-name=prod_portal
```

Deprecating an API product version on a portal:

```bash

# Deprecate on Dev portal
python3 main.py --oas_spec=../oasv1.yaml --konnect-portal-name=dev_portal --deprecate
```

Unpublishing an API product version from a portal:

```bash

# Unpublish on Dev portal
python3 main.py --oas_spec=../oasv1.yaml --konnect-portal-name=dev_portal --unpublish
```
