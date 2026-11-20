import schemathesis
from schemathesis import checks
from openapi_spec_validator import validate
from app.main import app
from app.config import settings

schema = schemathesis.openapi.from_asgi("/openapi.json", app).include(method="GET")


@schema.parametrize()
def test_api_conformance(case):
    headers = case.headers or {}
    headers["Authorization"] = f"Bearer {settings.admin_token}"

    response = case.call(headers=headers)

    case.validate_response(
        response,
        checks=(
            checks.not_a_server_error,
            checks.status_code_conformance,
            checks.response_schema_conformance,
        ),
    )


def test_openapi_document_is_valid_spec(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    spec = response.json()
    # Raises an exception if the generated document violates the OpenAPI spec
    validate(spec)


def test_openapi_publishes_expected_paths_methods_and_statuses(client):
    spec = client.get("/openapi.json").json()
    paths = spec["paths"]

    # Expected paths and HTTP methods
    assert {"get", "post"}.issubset(paths["/members"].keys())
    assert {"get", "put", "delete"}.issubset(paths["/members/{member_id}"].keys())
    assert "get" in paths["/members/{member_id}/books"]
    assert {"get", "post"}.issubset(paths["/books"].keys())
    assert {"get", "put", "delete"}.issubset(paths["/books/{book_id}"].keys())

    # Representative success and error status codes
    assert {"201", "401", "403", "409", "422"}.issubset(paths["/members"]["post"]["responses"].keys())
    assert {"200", "401", "404", "422"}.issubset(paths["/members/{member_id}"]["get"]["responses"].keys())
    assert {"204", "401", "403", "404", "409"}.issubset(paths["/members/{member_id}"]["delete"]["responses"].keys())
    assert {"201", "401", "403", "404", "409", "422"}.issubset(paths["/books"]["post"]["responses"].keys())

    # Request and response schemas published
    schemas = spec["components"]["schemas"]
    for name in ("MemberInput", "MemberResponse", "BookInput", "BookResponse"):
        assert name in schemas


def test_openapi_publishes_http_bearer_security_contract(client):
    spec = client.get("/openapi.json").json()
    security_schemes = spec["components"]["securitySchemes"]

    assert "HTTPBearer" in security_schemes
    assert security_schemes["HTTPBearer"]["type"] == "http"
    assert security_schemes["HTTPBearer"]["scheme"] == "bearer"

    # Protected routes require HTTPBearer
    assert {"HTTPBearer": []} in spec["paths"]["/members"]["get"]["security"]
    assert {"HTTPBearer": []} in spec["paths"]["/books"]["post"]["security"]

    # Public routes do not require authentication
    assert "security" not in spec["paths"]["/"]["get"]
    assert "security" not in spec["paths"]["/health"]["get"]