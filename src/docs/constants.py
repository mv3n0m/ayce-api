from .helpers import build_response_docs


def build_route_attrs(route, url_prefix, title="", success_status_code=200):
    url_prefix = url_prefix.removeprefix("/")
    if not url_prefix:
        return None

    return {
        "title": f"- {title}",
        "description": None,
        "tags": [url_prefix.title()],
        "responses": build_response_docs([
            {
                "status_code": success_status_code,
                "description": "success message",
                "_type": "object",
            },
            {
                "status_code": "4xx, 500",
                "description": "error message",
                "_type": "object",
            },
        ])
    }



route_attrs = {
    "/users": {
         "/register": build_route_attrs("/register", "/users", "for registering a new user.", 201),
        "/verify": build_route_attrs("/verify", "/users", "for verifying a user's email."),
        "/login": build_route_attrs("/login", "/users", "for user login."),
        "/request-password-reset": build_route_attrs("/request-password-reset", "/users", "for requesting a password reset."),
        "/reset-password": build_route_attrs("/reset-password", "/users", "for confirming a password reset."),
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