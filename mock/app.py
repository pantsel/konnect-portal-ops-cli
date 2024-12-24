from flask import Flask, jsonify, request
from flask_openapi3 import OpenAPI
import yaml
import uuid
import json
import base64

# Load OpenAPI Spec
def load_openapi_spec(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

spec = load_openapi_spec("mock/specs/api_products.yaml")

app = OpenAPI(__name__, info=spec['info'])

# In-memory data stores
data_stores = {
    "portals": {"data": [{
        "id": "66445d7c-c4aa-40d5-a683-97a5de16cd55",
        "name": "test-portal",
        "description": "My Portal Description"
    }]},
    "api_products": {"data": []},
    "api_product_versions": {"data": []},
    "api_product_version_specifications": {"data": []},
    "api_product_documents": {"data": []},
    "portal_product_versions": {"data": []}
}

# Helper functions
def generate_uuid():
    return str(uuid.uuid4())

def decode_base64(content):
    return base64.b64decode(content).decode('utf-8')

def get_filtered_data(store, filter_key, filter_value):
    return [item for item in data_stores[store]["data"] if item[filter_key] == filter_value]

def get_item_by_key(store, key, value):
    for item in data_stores[store]["data"]:
        if item[key] == value:
            return item
    return None

def create_item(store, item):
    item["id"] = generate_uuid()
    data_stores[store]["data"].append(item)
    return item

def update_item(store, key, value, updates):
    item = get_item_by_key(store, key, value)
    if item:
        item.update(updates)
        return item
    return None

def delete_item(store, item_id):
    item = get_item_by_key(store, "id", item_id)
    if item:
        data_stores[store]["data"].remove(item)
        return True
    return False

# Endpoint handlers
def handle_get_api_products():
    if request.args.get("filter[name]"):
        filtered_products = get_filtered_data("api_products", "name", request.args.get("filter[name]"))
        return jsonify({"data": filtered_products}), 200
    return jsonify(data_stores["api_products"]), 200

def handle_post_api_products():
    item = create_item("api_products", request.json)
    return jsonify(item), 201

def handle_patch_api_products(id):
    item = update_item("api_products", "id", id, request.json)
    if item:
        return jsonify(item)
    return jsonify({"message": "Product not found"}), 404

def handle_delete_api_products(id):
    if delete_item("api_products", id):
        return jsonify({"message": "Product deleted"}), 204
    return jsonify({"message": "Product not found"}), 404

def handle_get_api_product_documents():
    return jsonify(data_stores["api_product_documents"]), 200

def handle_get_api_product_document(id):
    item = get_item_by_key("api_product_documents", "id", id)
    if item:
        return jsonify(item)
    return jsonify({"message": "Document not found"}), 404

def handle_post_api_product_documents():
    request.json["content"] = decode_base64(request.json["content"])
    item = create_item("api_product_documents", request.json)
    return jsonify(item), 201

def handle_patch_api_product_document(id):
    item = update_item("api_product_documents", "id", id, request.json)
    if item:
        return jsonify(item)
    return jsonify({"message": "Document not found"}), 404

def handle_delete_api_product_document(id):
    if delete_item("api_product_documents", id):
        return jsonify({"message": "Document deleted"}), 204
    return jsonify({"message": "Document not found"}), 404

def handle_get_api_product_versions():
    if request.args.get("filter[name]"):
        filtered_versions = get_filtered_data("api_product_versions", "name", request.args.get("filter[name]"))
        return jsonify({"data": filtered_versions}), 200
    return jsonify(data_stores["api_product_versions"]), 200

def handle_get_api_product_version(id):
    item = get_item_by_key("api_product_versions", "id", id)
    if item:
        return jsonify(item)
    return jsonify({"message": "Version not found"}), 404

def handle_post_api_product_versions():
    item = create_item("api_product_versions", request.json)
    return jsonify(item), 201

def handle_patch_api_product_version(id):
    item = update_item("api_product_versions", "id", id, request.json)
    if item:
        return jsonify(item)
    return jsonify({"message": "Version not found"}), 404

def handle_delete_api_product_version(id):
    if delete_item("api_product_versions", id):
        return jsonify({"message": "Version deleted"}), 204
    return jsonify({"message": "Version not found"}), 404

def handle_get_api_product_version_specifications():
    return jsonify(data_stores["api_product_version_specifications"]), 200

def handle_get_api_product_version_specification(id):
    item = get_item_by_key("api_product_version_specifications", "id", id)
    if item:
        return jsonify(item)
    return jsonify({"message": "Specification not found"}), 404

def handle_post_api_product_version_specifications():
    request.json["content"] = decode_base64(request.json["content"])
    item = create_item("api_product_version_specifications", request.json)
    return jsonify(item), 201

def handle_patch_api_product_version_specification(id):
    item = update_item("api_product_version_specifications", "id", id, request.json)
    if item:
        return jsonify(item)
    return jsonify({"message": "Specification not found"}), 404

def handle_delete_api_product_version_specification(id):
    if delete_item("api_product_version_specifications", id):
        return jsonify({"message": "Specification deleted"}), 204
    return jsonify({"message": "Specification not found"}), 404

# Define Mock Endpoints from OpenAPI Spec
base_path = "/" + spec.get("servers", [{}])[0].get("url", "").rstrip("/").split("/")[-1]

def create_mock_function(route, method):
    def mock_endpoint(**kwargs):
        if method.upper() == "GET":
            if route == "/api-products":
                return handle_get_api_products()
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
    return jsonify(data_stores["portals"]), 200

@app.route("/v2/portals/<portalId>/product-versions", methods=["GET"])
def get_portal_product_versions(portalId):
    if request.args.get("filter[product_version_id]"):
        filtered_portal_product_versions = get_filtered_data("portal_product_versions", "product_version_id", request.args.get("filter[product_version_id]"))
        for version in filtered_portal_product_versions:
            version["auth_strategies"] = [{"id": id, "name": "auth_strategy_name"} for id in version["auth_strategy_ids"]]
        return jsonify({"data": filtered_portal_product_versions}), 200
    return jsonify(data_stores["portal_product_versions"]), 200

@app.route("/v2/portals/<portalId>/product-versions", methods=["POST"])
def create_portal_product_version(portalId):
    item = create_item("portal_product_versions", request.json)
    print(json.dumps(data_stores["portal_product_versions"], indent=2))
    return jsonify(item), 201

@app.route("/v2/portals/<portalId>/product-versions/<id>", methods=["PATCH"])
def update_portal_product_version(portalId, id):
    item = update_item("portal_product_versions", "product_version_id", id, request.json)
    print(json.dumps(data_stores["portal_product_versions"], indent=2))
    if item:
        return jsonify(item)
    return jsonify({"message": "Portal Product Version not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8080", debug=True)
