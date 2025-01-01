import unittest
from uuid import uuid4
from kptl.helpers.validator import ProductStateValidator

class TestProductStateValidator(unittest.TestCase):

    def test_valid_schema(self):
        portal_id = str(uuid4())
        schema = {
            "_version": "1.0.0",
            "info": {
                "name": "Test Product",
                "description": "A test product"
            },
            "documents": {
                "sync": True,
                "dir": "docs"
            },
            "portals": [
                {
                    "portal_id": portal_id,
                    "portal_name": "Test Portal"
                }
            ],
            "versions": [
                {
                    "name": "v1",
                    "spec": "spec-v1",
                    "portals": [
                        {
                            "portal_id": portal_id
                        }
                    ],
                    "gateway_service": {
                        "id": str(uuid4()),
                        "control_plane_id": str(uuid4())
                    }
                }
            ]
        }
        validator = ProductStateValidator(schema)
        is_valid, errors = validator.validate()
        self.assertTrue(is_valid)
        self.assertIsNone(errors)

    def test_invalid_version(self):
        schema = {
            "_version": "invalid_version",
            "info": {
                "name": "Test Product"
            }
        }
        validator = ProductStateValidator(schema)
        is_valid, errors = validator.validate()
        self.assertFalse(is_valid)
        self.assertIn("Invalid or missing '_version'", errors)

    def test_missing_info(self):
        schema = {
            "_version": "1.0.0"
        }
        validator = ProductStateValidator(schema)
        is_valid, errors = validator.validate()
        self.assertFalse(is_valid)
        self.assertIn("Missing or invalid 'info'", errors)

    def test_invalid_portal(self):
        schema = {
            "_version": "1.0.0",
            "info": {
                "name": "Test Product"
            },
            "portals": [
                {
                    "portal_id": "invalid_uuid"
                }
            ]
        }
        validator = ProductStateValidator(schema)
        is_valid, errors = validator.validate()
        self.assertFalse(is_valid)
        self.assertIn("The 'portal_id' in 'portals[0]' is not a valid UUID.", errors)

    def test_invalid_gateway_service(self):
        schema = {
            "_version": "1.0.0",
            "info": {
                "name": "Test Product"
            },
            "portals": [],
            "versions": [
                {
                    "name": "v1",
                    "spec": "spec-v1",
                    "gateway_service": {
                        "id": "invalid_uuid",
                        "control_plane_id": str(uuid4())
                    }
                }
            ]
        }
        validator = ProductStateValidator(schema)
        is_valid, errors = validator.validate()
        self.assertFalse(is_valid)
        self.assertIn("The 'id' in 'versions[0].gateway_service' is not a valid UUID.", errors)


    def test_invalid_publish_status(self):
        schema = {
            "_version": "1.0.0",
            "info": {
                "name": "Test Product"
            },
            "portals": [
                {
                    "portal_id": str(uuid4()),
                    "portal_name": "Test Portal"
                }
            ],
            "versions": [
                {
                    "name": "v1",
                    "spec": "spec-v1",
                    "portals": [
                        {
                            "portal_name": "Test Portal",
                            "publish_status": "invalid_status"
                        }
                    ]
                }
            ]
        }
        validator = ProductStateValidator(schema)
        is_valid, errors = validator.validate()
        self.assertFalse(is_valid)

    def test_invalid_application_registration_enabled(self):
        schema = {
            "_version": "1.0.0",
            "info": {
                "name": "Test Product"
            },
            "portals": [
                {
                    "portal_id": str(uuid4()),
                    "portal_name": "Test Portal"
                }
            ],
            "versions": [
                {
                    "name": "v1",
                    "spec": "spec-v1",
                    "portals": [
                        {
                            "portal_name": "Test Portal",
                            "application_registration_enabled": "not_a_boolean"
                        }
                    ]
                }
            ]
        }
        validator = ProductStateValidator(schema)
        is_valid, errors = validator.validate()
        self.assertFalse(is_valid)

    def test_invalid_auto_approve_registration(self):
        schema = {
            "_version": "1.0.0",
            "info": {
                "name": "Test Product"
            },
            "portals": [
                {
                    "portal_id": str(uuid4()),
                    "portal_name": "Test Portal"
                }
            ],
            "versions": [
                {
                    "name": "v1",
                    "spec": "spec-v1",
                    "portals": [
                        {
                            "portal_name": "Test Portal",
                            "auto_approve_registration": "not_a_boolean"
                        }
                    ]
                }
            ]
        }
        validator = ProductStateValidator(schema)
        is_valid, errors = validator.validate()
        self.assertFalse(is_valid)

    def test_invalid_auth_strategies(self):
        schema = {
            "_version": "1.0.0",
            "info": {
                "name": "Test Product"
            },
            "portals": [
                {
                    "portal_id": str(uuid4()),
                    "portal_name": "Test Portal"
                }
            ],
            "versions": [
                {
                    "name": "v1",
                    "spec": "spec-v1",
                    "portals": [
                        {
                            "portal_name": "Test Portal",
                            "auth_strategies": "not_a_list"
                        }
                    ]
                }
            ]
        }
        validator = ProductStateValidator(schema)
        is_valid, errors = validator.validate()
        self.assertFalse(is_valid)

    def test_invalid_auth_strategy_id(self):
        schema = {
            "_version": "1.0.0",
            "info": {
                "name": "Test Product"
            },
            "portals": [
                {
                    "portal_id": str(uuid4()),
                    "portal_name": "Test Portal"
                }
            ],
            "versions": [
                {
                    "name": "v1",
                    "spec": "spec-v1",
                    "portals": [
                        {
                            "portal_name": "Test Portal",
                            "auth_strategies": [
                                {
                                    "id": "invalid_uuid"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        validator = ProductStateValidator(schema)
        is_valid, errors = validator.validate()
        self.assertFalse(is_valid)

if __name__ == '__main__':
    unittest.main()
