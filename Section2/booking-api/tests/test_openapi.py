def test_openapi_documents_bearer_auth_and_responses(client):
    document = client.get("/openapi.json").json()
    event_post = document["paths"]["/events"]["post"]
    assert "201" in event_post["responses"]
    assert "422" in event_post["responses"]
    assert document["components"]["securitySchemes"]["OAuth2PasswordBearer"]["type"] == "oauth2"
    assert "/auth/token" in document["paths"]
