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
    "api_products": {"data": []},
    "api_product_versions": {"data": []},
    "api_product_version_specifications": {"data": []},
    "api_product_documents": {"data": []},
    "portal_product_versions": {"data": []}
}

# Utility functions
def generate_uuid():
    return str(uuid.uuid4())

def decode_base64(content):
    return base64.b64decode(content).decode('utf-8')

def find_item_by_id(data_store, item_id):
    return next((item for item in data_store["data"] if item["id"] == item_id), None)

def filter_items_by_name(data_store, name):
    return [item for item in data_store["data"] if item["name"] == name]

def print_datastore(data_store_name):
    print(f"Updated {data_store_name}:")
    print(json.dumps(data_stores[data_store_name], indent=2))

# Route handlers
def handle_get_request(data_store, filter_key=None):
    if filter_key and request.args.get(filter_key):
        filtered_items = filter_items_by_name(data_store, request.args.get(filter_key))
        response_data = {"data": filtered_items}
        print(json.dumps(response_data, indent=2))
        return jsonify({"data": filtered_items}), 200
    return jsonify(data_store), 200

def handle_post_request(data_store, data_store_name):
    item = request.json
    item["id"] = generate_uuid()
    if "content" in item:
        item["content"] = decode_base64(item["content"])
    data_store["data"].append(item)
    print_datastore(data_store_name)
    return jsonify(item), 201

def handle_patch_request(data_store, item_id, data_store_name):
    item = find_item_by_id(data_store, item_id)
    if item:
        item.update(request.json)
        print_datastore(data_store_name)
        return jsonify(item)
    return jsonify({"message": "Item not found"}), 404

def handle_delete_request(data_store, item_id, data_store_name):
    item = find_item_by_id(data_store, item_id)
    if item:
        data_store["data"].remove(item)
        print_datastore(data_store_name)
        return jsonify({"message": "Item deleted"}), 204
    return jsonify({"message": "Item not found"}), 404

# Define Mock Endpoints from OpenAPI Spec
base_path = "/" + spec.get("servers", [{}])[0].get("url", "").rstrip("/").split("/")[-1]

for path, methods in spec.get("paths", {}).items():
    for method, details in methods.items():
        route = path.replace("{", "<").replace("}", ">")  # Convert OpenAPI paths to Flask format

        def create_mock_function(route, method):
            def mock_endpoint(**kwargs):
                if method.upper() == "GET":
                    if route == "/api-products":
                        return handle_get_request(data_stores["api_products"], "filter[name]")
                    if route == "/api-products/<id>":
                        return handle_get_request(data_stores["api_products"])
                    if route == "/api-products/<apiProductId>/documents":
                        return handle_get_request(data_stores["api_product_documents"])
                    if route == "/api-products/<apiProductId>/documents/<id>":
                        return handle_get_request(data_stores["api_product_documents"])
                    if route == "/api-products/<apiProductId>/product-versions":
                        return handle_get_request(data_stores["api_product_versions"], "filter[name]")
                    if route == "/api-products/<apiProductId>/product-versions/<id>":
                        return handle_get_request(data_stores["api_product_versions"])
                    if route == "/api-products/<apiProductId>/product-versions/<apiProductVersionId>/specifications":
                        return handle_get_request(data_stores["api_product_version_specifications"])
                    if route == "/api-products/<apiProductId>/product-versions/<apiProductVersionId>/specifications/<id>":
                        return handle_get_request(data_stores["api_product_version_specifications"])

                if method.upper() == "POST":
                    if route == "/api-products":
                        return handle_post_request(data_stores["api_products"], "api_products")
                    if route == "/api-products/<apiProductId>/documents":
                        return handle_post_request(data_stores["api_product_documents"], "api_product_documents")
                    if route == "/api-products/<apiProductId>/product-versions":
                        return handle_post_request(data_stores["api_product_versions"], "api_product_versions")
                    if route == "/api-products/<apiProductId>/product-versions/<apiProductVersionId>/specifications":
                        return handle_post_request(data_stores["api_product_version_specifications"], "api_product_version_specifications")

                if method.upper() == "PATCH":
                    if route == "/api-products/<id>":
                        return handle_patch_request(data_stores["api_products"], kwargs["id"], "api_products")
                    if route == "/api-products/<apiProductId>/documents/<id>":
                        return handle_patch_request(data_stores["api_product_documents"], kwargs["id"], "api_product_documents")
                    if route == "/api-products/<apiProductId>/product-versions/<id>":
                        return handle_patch_request(data_stores["api_product_versions"], kwargs["id"], "api_product_versions")
                    if route == "/api-products/<apiProductId>/product-versions/<apiProductVersionId>/specifications/<id>":
                        return handle_patch_request(data_stores["api_product_version_specifications"], kwargs["id"], "api_product_version_specifications")

                if method.upper() == "DELETE":
                    if route == "/api-products/<id>":
                        return handle_delete_request(data_stores["api_products"], kwargs["id"], "api_products")
                    if route == "/api-products/<apiProductId>/documents/<id>":
                        return handle_delete_request(data_stores["api_product_documents"], kwargs["id"], "api_product_documents")
                    if route == "/api-products/<apiProductId>/product-versions/<id>":
                        return handle_delete_request(data_stores["api_product_versions"], kwargs["id"], "api_product_versions")
                    if route == "/api-products/<apiProductId>/product-versions/<apiProductVersionId>/specifications/<id>":
                        return handle_delete_request(data_stores["api_product_version_specifications"], kwargs["id"], "api_product_version_specifications")

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

        prefixed_route = "/" + base_path + route
        print(f"Creating {method.upper()} route for {prefixed_route}")
        mock_function = create_mock_function(route, method)
        endpoint_name = f"{method}_{prefixed_route}"  # Ensure unique endpoint name
        app.route(prefixed_route, methods=[method.upper()], endpoint=endpoint_name)(mock_function)

# Portal routes
@app.route("/v2/portals", methods=["GET"])
def get_portals():
    return jsonify({"data": [{
        "id": generate_uuid(),
        "name": "dev_portal",
        "description": "My Portal Description"
    }]})

@app.route("/v2/portals/<portalId>/product-versions", methods=["GET"])
def get_portal_product_versions(portalId):
    if request.args.get("filter[product_version_id]"):
        filtered_portal_product_versions = [v for v in data_stores["portal_product_versions"]["data"] if v["product_version_id"] == request.args.get("filter[product_version_id]")]
        for version in filtered_portal_product_versions:
            version["auth_strategies"] = [{"id": id, "name": "auth_strategy_name"} for id in version["auth_strategy_ids"]]
        return jsonify({"data": filtered_portal_product_versions}), 200
    return jsonify(data_stores["portal_product_versions"]), 200

@app.route("/v2/portals/<portalId>/product-versions", methods=["POST"])
def create_portal_product_version(portalId):
    item = request.json
    item["id"] = generate_uuid()
    data_stores["portal_product_versions"]["data"].append(item)
    print_datastore("portal_product_versions")
    return jsonify(item), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8080", debug=True)
