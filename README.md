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

Publish oas.yaml to Konnect Portals:

```bash
# Dev portal
python3 main.py --oas_spec=../oas.yaml --environment=dev 

# Prod portal
python3 main.py --oas_spec=../oas.yaml --environment=prod
```

Publish a new version of an existing API (oas2.yaml) to Konnect Portals:

```bash
# Dev portal
python3 main.py --oas_spec=../oas2.yaml --environment=dev

# Prod portal
python3 main.py --oas_spec=../oas2.yaml --environment=prod
```