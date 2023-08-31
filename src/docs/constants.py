from .helpers import build_response_docs


route_attrs = {
    "/test-route": {
        "title": "Test route",
        "tags": ["Test"],
        "responses": build_response_docs([
            {
                "status_code": 200,
                "description": "Test message",
                "_type": "string"
            }
        ])
    },
    # Users
    "/register": {
        "title": "- for registering a new user.",
        "description": None,
        "tags": ["Users"],
        "responses": build_response_docs([
            {
                "status_code": 201,
                "description": "success message",
                "_type": "object"
            },
            {
                "status_code": "4xx, 500",
                "description": "error message",
                "_type": "object"
            }
        ])
    },
    "/verify": {
        "title": "- for verifying a user's email.",
        "description": None,
        "tags": ["Users"],
        "responses": build_response_docs([
            {
                "status_code": 200,
                "description": "success message",
                "_type": "object",
            },
            {
                "status_code": "4xx, 500",
                "description": "error message",
                "_type": "object",
            },
        ])
    },
    "/login": {
        "title": "- for user login.",
        "description": None,
        "tags": ["Users"],
        "responses": build_response_docs([
            {
                "status_code": 200,
                "description": "success message",
                "_type": "object",
            },
            {
                "status_code": "4xx, 500",
                "description": "error message",
                "_type": "object",
            },
        ])
    },
    "/request-password-reset": {
        "title": "- for requesting a password reset.",
        "description": None,
        "tags": ["Users"],
        "responses": build_response_docs([
            {
                "status_code": 200,
                "description": "success message",
                "_type": "object",
            },
            {
                "status_code": "4xx, 500",
                "description": "error message",
                "_type": "object",
            },
        ])
    },
    "/reset-password": {
        "title": "- for confirming a password reset.",
        "description": None,
        "tags": ["Users"],
        "responses": build_response_docs([
            {
                "status_code": 200,
                "description": "success message",
                "_type": "object",
            },
            {
                "status_code": "4xx, 500",
                "description": "error message",
                "_type": "object",
            },
        ])
    },
    # Developers
    "/add-api-key": {
        "title": "- for adding a new API key for developers.",
        "description": None,
        "tags": ["Developers"],
        "responses": build_response_docs([
            {
                "status_code": 201,
                "description": "success message",
                "_type": "object",
            },
            {
                "status_code": "4xx, 500",
                "description": "error message",
                "_type": "object",
            },
        ])
    },
    "/add-api-key/otp-confirm": {
        "title": "- for confirmation of the addition of new API key.",
        "description": None,
        "tags": ["Developers"],
        "responses": build_response_docs([
            {
                "status_code": 200,
                "description": "success message",
                "_type": "object",
            },
            {
                "status_code": "4xx, 500",
                "description": "error message",
                "_type": "object",
            },
        ])
    },
    "/list-api-keys": {
        "title": "- for listing all the API keys under an account.",
        "description": None,
        "tags": ["Developers"],
        "responses": build_response_docs([
            {
                "status_code": 200,
                "description": "success message",
                "_type": "object",
            },
            {
                "status_code": "4xx, 500",
                "description": "error message",
                "_type": "object",
            },
        ])
    },
    "/revoke-api-key": {
        "title": "- for revoking an API key.",
        "description": None,
        "tags": ["Developers"],
        "responses": build_response_docs([
            {
                "status_code": 200,
                "description": "success message",
                "_type": "object",
            },
            {
                "status_code": "4xx, 500",
                "description": "error message",
                "_type": "object",
            },
        ])
    },
    "/generate-ecommerce-key": {
        "title": "- for generating an instant e-commerce key.",
        "description": None,
        "tags": ["Developers"],
        "responses": build_response_docs([
            {
                "status_code": 201,
                "description": "success message",
                "_type": "object",
            },
            {
                "status_code": "4xx, 500",
                "description": "error message",
                "_type": "object",
            },
        ])
    },
    "/webhook-simulator": {
        "title": "- for simulating endpoint calls.",
        "description": None,
        "tags": ["Developers"],
        "responses": build_response_docs([
            {
                "status_code": 200,
                "description": "success message",
                "_type": "object",
            },
            {
                "status_code": "4xx, 500",
                "description": "error message",
                "_type": "object",
            },
        ])
    },
    # Account Data
    "/business-details": {
        "title": "- for adding business details.",
        "description": None,
        "tags": ["User Profile"],
        "responses": build_response_docs([
            {
                "status_code": 201,
                "description": "success message",
                "_type": "object",
            },
            {
                "status_code": "4xx, 500",
                "description": "error message",
                "_type": "object",
            },
        ])
    },
    "/settlement-billing": {
        "title": "- for adding settlement/billing details.",
        "description": None,
        "tags": ["User Profile"],
        "responses": build_response_docs([
            {
                "status_code": 201,
                "description": "success message",
                "_type": "object",
            },
            {
                "status_code": "4xx, 500",
                "description": "error message",
                "_type": "object",
            },
        ])
    },
    "/authorized-representative": {
        "title": "- for adding authorized representative details.",
        "description": None,
        "tags": ["User Profile"],
        "responses": build_response_docs([
            {
                "status_code": 201,
                "description": "success message",
                "_type": "object",
            },
            {
                "status_code": "4xx, 500",
                "description": "error message",
                "_type": "object",
            },
        ])
    },
    "/beneficial-owner": {
        "title": "- for adding beneficial owner details.",
        "description": None,
        "tags": ["User Profile"],
        "responses": build_response_docs([
            {
                "status_code": 201,
                "description": "success message",
                "_type": "object",
            },
            {
                "status_code": "4xx, 500",
                "description": "error message",
                "_type": "object",
            },
        ])
    },
    "/fetch-profile-data": {
        "title": "- for fetching profile data of a user.",
        "description": None,
        "tags": ["User Profile"],
        "responses": build_response_docs([
            {
                "status_code": 200,
                "description": "success message",
                "_type": "object",
            },
            {
                "status_code": "4xx, 500",
                "description": "error message",
                "_type": "object",
            },
        ])
    },
    "/submit-details-confirmation": {
        "title": "- for submitting confirmation of the profile details.",
        "description": None,
        "tags": ["User Profile"],
        "responses": build_response_docs([
            {
                "status_code": 200,
                "description": "success message",
                "_type": "object",
            },
            {
                "status_code": "4xx, 500",
                "description": "error message",
                "_type": "object",
            },
        ])
    },
}