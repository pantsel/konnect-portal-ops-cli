"""
This module provides a mock implementation of the Konnect API using Flask and OpenAPI.
It includes endpoints for managing portals, API products, product versions, and related documents.
"""

import uuid
import base64
from flask import jsonify, request
from flask_openapi3 import OpenAPI
import yaml

# Load OpenAPI Spec
def load_openapi_spec(file_path):
    """Load OpenAPI specification from a YAML file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

spec = load_openapi_spec("mock/specs/api_products.yaml")

app = OpenAPI(__name__, info=spec['info'])

# In-memory data stores
data_stores = {
    "portals": {"data": [{
        "id": "66445d7c-c4aa-40d5-a683-97a5de16cd55",
        "name": "dev_portal",
        "description": "My Development Portal"
    },{
        "id": "4162d3be-5c74-45f8-9a10-0c78867f6729",
        "name": "prod_portal",
        "description": "My Production Portal"
    }]},
    "api_products": {"data": []},
    "api_product_versions": {"data": []},
    "api_product_version_specifications": {"data": []},
    "api_product_documents": {"data": []},
    "portal_product_versions": {"data": []}
}

# Helper functions
def generate_uuid():
    """Generate a new UUID."""
    return str(uuid.uuid4())

def decode_base64(content):
    """Decode a base64 encoded string."""
    return base64.b64decode(content).decode('utf-8')

def get_filtered_data(store, filters):
    """Get filtered data from a store based on multiple key-value pairs."""
    return [item for item in data_stores[store]["data"] if all(item.get(k) == v for k, v in filters.items())]

def get_item_by_key(store, key, value):
    """Get an item from a store by key and value."""
    for item in data_stores[store]["data"]:
        if item[key] == value:
            return item
    return None

def get_item_by_keys(store, key_values):
    """Get an item from a store by multiple key-value pairs."""
    for item in data_stores[store]["data"]:
        if all(item.get(k) == v for k, v in key_values.items()):
            return item
    return None

def create_item(store, item):
    """Create a new item in a store."""
    item["id"] = generate_uuid()
    data_stores[store]["data"].append(item)
    return item

def update_item(store, key_values, updates):
    """Update an item in a store."""
    item = get_item_by_keys(store, key_values)
    if item:
        item.update(updates)
        return item
    return None

def delete_item(store, item_id):
    """Delete an item from a store."""
    item = get_item_by_key(store, "id", item_id)
    if item:
        data_stores[store]["data"].remove(item)
        return True
    return False

# Endpoint handlers
def handle_get_api_products():
    """Handle GET requests for API products."""
    if request.args.get("filter[name]"):
        filtered_products = get_filtered_data("api_products", {"name": request.args.get("filter[name]")})
        return jsonify({"data": filtered_products}), 200
    return jsonify(data_stores["api_products"]), 200

def handle_get_api_product_by_id(product_id):
    """Handle GET requests for a specific API product by ID."""
    item = get_item_by_key("api_products", "id", product_id)
    if item:
        return jsonify(item)
    return jsonify({"message": "Product not found"}), 404

def handle_post_api_products():
    """Handle POST requests to create a new API product."""
    item = create_item("api_products", request.json)
    return jsonify(item), 201

def handle_patch_api_products(product_id):
    """Handle PATCH requests to update an API product."""
    item = update_item("api_products", {"id": product_id}, request.json)
    if item:
        return jsonify(item)
    return jsonify({"message": "Product not found"}), 404

def handle_delete_api_products(product_id):
    """Handle DELETE requests to remove an API product."""
    if delete_item("api_products", product_id):
        return jsonify({"message": "Product deleted"}), 204
    return jsonify({"message": "Product not found"}), 404

def handle_get_api_product_documents():
    """Handle GET requests for API product documents."""
    return jsonify(data_stores["api_product_documents"]), 200

def handle_get_api_product_document(document_id):
    """Handle GET requests for a specific API product document by ID."""
    item = get_item_by_key("api_product_documents", "id", document_id)
    if item:
        return jsonify(item)
    return jsonify({"message": "Document not found"}), 404

def handle_post_api_product_documents():
    """Handle POST requests to create a new API product document."""
    request.json["content"] = decode_base64(request.json["content"])
    item = create_item("api_product_documents", request.json)
    return jsonify(item), 201

def handle_patch_api_product_document(document_id):
    """Handle PATCH requests to update an API product document."""
    item = update_item("api_product_documents", {"id": document_id}, request.json)
    if item:
        return jsonify(item)
    return jsonify({"message": "Document not found"}), 404

def handle_delete_api_product_document(document_id):
    """Handle DELETE requests to remove an API product document."""
    if delete_item("api_product_documents", document_id):
        return jsonify({"message": "Document deleted"}), 204
    return jsonify({"message": "Document not found"}), 404

def handle_get_api_product_versions():
    """Handle GET requests for API product versions."""
    if request.args.get("filter[name]"):
        filtered_versions = get_filtered_data("api_product_versions", {"name": request.args.get("filter[name]")})
        return jsonify({"data": filtered_versions}), 200
    return jsonify(data_stores["api_product_versions"]), 200

def handle_get_api_product_version(version_id):
    """Handle GET requests for a specific API product version by ID."""
    item = get_item_by_key("api_product_versions", "id", version_id)
    if item:
        return jsonify(item)
    return jsonify({"message": "Version not found"}), 404

def handle_post_api_product_versions():
    """Handle POST requests to create a new API product version."""
    item = create_item("api_product_versions", request.json)
    return jsonify(item), 201

def handle_patch_api_product_version(version_id):
    """Handle PATCH requests to update an API product version."""
    item = update_item("api_product_versions", {"id": version_id}, request.json)
    if item:
        return jsonify(item)
    return jsonify({"message": "Version not found"}), 404

def handle_delete_api_product_version(version_id):
    """Handle DELETE requests to remove an API product version."""
    if delete_item("api_product_versions", version_id):
        return jsonify({"message": "Version deleted"}), 204
    return jsonify({"message": "Version not found"}), 404

def handle_get_api_product_version_specifications():
    """Handle GET requests for API product version specifications."""
    return jsonify(data_stores["api_product_version_specifications"]), 200

def handle_get_api_product_version_specification(specification_id):
    """Handle GET requests for a specific API product version specification by ID."""
    item = get_item_by_key("api_product_version_specifications", "id", specification_id)
    if item:
        return jsonify(item)
    return jsonify({"message": "Specification not found"}), 404

def handle_post_api_product_version_specifications():
    """Handle POST requests to create a new API product version specification."""
    request.json["content"] = decode_base64(request.json["content"])
    item = create_item("api_product_version_specifications", request.json)
    return jsonify(item), 201

def handle_patch_api_product_version_specification(specification_id):
    """Handle PATCH requests to update an API product version specification."""
    item = update_item("api_product_version_specifications", {"id": specification_id}, request.json)
    if item:
        return jsonify(item)
    return jsonify({"message": "Specification not found"}), 404

def handle_delete_api_product_version_specification(specification_id):
    """Handle DELETE requests to remove an API product version specification."""
    if delete_item("api_product_version_specifications", specification_id):
        return jsonify({"message": "Specification deleted"}), 204
    return jsonify({"message": "Specification not found"}), 404

# Define Mock Endpoints from OpenAPI Spec
base_path = "/" + spec.get("servers", [{}])[0].get("url", "").rstrip("/").split("/")[-1]

def create_mock_function(route, method):
    """Create a mock endpoint function."""
    def mock_endpoint(**kwargs):
        if method.upper() == "GET":
            if route == "/api-products":
                return handle_get_api_products()
            if route == "/api-products/<id>":
                return handle_get_api_product_by_id(kwargs["id"])
            if route == "/api-products/<apiProductId>/documents":
                return handle_get_api_product_documents()
            if route == "/api-products/<apiProductId>/documents/<id>":
                return handle_get_api_product_document(kwargs["id"])
            if route == "/api-products/<apiProductId>/product-versions":
                return handle_get_api_product_versions()
            if route == "/api-products/<apiProductId>/product-versions/<id>":
                return handle_get_api_product_version(kwargs["id"])
            if route == "/api-products/<apiProductId>/product-versions/<apiProductVersionId>/specifications":
                return handle_get_api_product_version_specifications()
            if route == "/api-products/<apiProductId>/product-versions/<apiProductVersionId>/specifications/<id>":
                return handle_get_api_product_version_specification(kwargs["id"])

        if method.upper() == "POST":
            if route == "/api-products":
                return handle_post_api_products()
            if route == "/api-products/<apiProductId>/documents":
                return handle_post_api_product_documents()
            if route == "/api-products/<apiProductId>/product-versions":
                return handle_post_api_product_versions()
            if route == "/api-products/<apiProductId>/product-versions/<apiProductVersionId>/specifications":
                return handle_post_api_product_version_specifications()

        if method.upper() == "PATCH":
            if route == "/api-products/<id>":
                return handle_patch_api_products(kwargs["id"])
            if route == "/api-products/<apiProductId>/documents/<id>":
                return handle_patch_api_product_document(kwargs["id"])
            if route == "/api-products/<apiProductId>/product-versions/<id>":
                return handle_patch_api_product_version(kwargs["id"])
            if route == "/api-products/<apiProductId>/product-versions/<apiProductVersionId>/specifications/<id>":
                return handle_patch_api_product_version_specification(kwargs["id"])

        if method.upper() == "DELETE":
            if route == "/api-products/<id>":
                return handle_delete_api_products(kwargs["id"])
            if route == "/api-products/<apiProductId>/documents/<id>":
                return handle_delete_api_product_document(kwargs["id"])
            if route == "/api-products/<apiProductId>/product-versions/<id>":
                return handle_delete_api_product_version(kwargs["id"])
            if route == "/api-products/<apiProductId>/product-versions/<apiProductVersionId>/specifications/<id>":
                return handle_delete_api_product_version_specification(kwargs["id"])

        # Generic endpoint for debugging
        return jsonify({
            "params": kwargs,
            "method": method,
            "body": request.json if request.data else {},
            "query": request.args,
            "headers": dict(request.headers),
            "path": request.path,
            "route": route
        })
    return mock_endpoint

for path, methods in spec.get("paths", {}).items():
    for method, details in methods.items():
        route = path.replace("{", "<").replace("}", ">")
        prefixed_route = "/" + base_path + route
        print(f"Creating {method.upper()} route for {prefixed_route}")
        mock_function = create_mock_function(route, method)
        endpoint_name = f"{method}_{prefixed_route}"
        app.route(prefixed_route, methods=[method.upper()], endpoint=endpoint_name)(mock_function)

# Portal routes
@app.route("/v2/portals", methods=["GET"])
def get_portals():
    """Get all portals or filter by name."""
    if request.args.get("filter[name]"):
        filtered_portals = get_filtered_data("portals", {"name": request.args.get("filter[name]")})
        return jsonify({"data": filtered_portals}), 200
    return jsonify(data_stores["portals"]), 200

@app.route("/v2/portals/<portal_id>/product-versions", methods=["GET"])
def get_portal_product_versions(portal_id):
    """Get product versions for a specific portal."""
    if request.args.get("filter[product_version_id]"):
        filtered_portal_product_versions = get_filtered_data("portal_product_versions", {
            "product_version_id": request.args.get("filter[product_version_id]"),
            "portal_id": portal_id
            })
        for version in filtered_portal_product_versions:
            version["auth_strategies"] = [{"id": id, "name": "auth_strategy_name"} for id in version["auth_strategy_ids"]]
        return jsonify({"data": filtered_portal_product_versions}), 200
    return jsonify({
        "data": get_filtered_data("portal_product_versions", {"portal_id": portal_id})
    }), 200

@app.route("/v2/portals/<portal_id>/product-versions", methods=["POST"])
def create_portal_product_version(portal_id):
    """Create a new product version for a specific portal."""
    request.json["portal_id"] = portal_id
    item = create_item("portal_product_versions", request.json)
    return jsonify(item), 201

@app.route("/v2/portals/<portal_id>/product-versions/<id>", methods=["PATCH"])
def update_portal_product_version(portal_id, id):
    """Update a product version for a specific portal."""
    item = update_item("portal_product_versions", {"product_version_id": id, "portal_id": portal_id}, request.json)
    if item:
        return jsonify(item)
    return jsonify({"message": "Portal Product Version not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8080", debug=True)
