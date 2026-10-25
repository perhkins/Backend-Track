def test_openapi_documents_role_headers_and_responses(client):
    document = client.get("/openapi.json").json()
    event_post = document["paths"]["/events"]["post"]
    assert "201" in event_post["responses"]
    assert "422" in event_post["responses"]
    assert "X-Role" in str(document)
