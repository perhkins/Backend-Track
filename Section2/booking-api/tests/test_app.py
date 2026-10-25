def test_health_and_openapi(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/").json()["docs"] == "/docs"
    assert client.get("/docs").status_code == 200
    assert client.get("/redoc").status_code == 200
    document = client.get("/openapi.json").json()
    assert "/events" in document["paths"]
    assert "/events/{event_id}/registrations" in document["paths"]
