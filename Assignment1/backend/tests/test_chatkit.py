from unittest.mock import MagicMock, patch


def make_client():
    from backend.app.main import app
    from fastapi.testclient import TestClient
    return TestClient(app)


def test_create_session_missing_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("CHATKIT_WORKFLOW_ID", raising=False)
    client = make_client()
    response = client.post("/api/create-session", json={})
    assert response.status_code == 500
    assert "OPENAI_API_KEY" in response.json()["error"]


def test_create_session_missing_workflow(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.delenv("CHATKIT_WORKFLOW_ID", raising=False)
    monkeypatch.delenv("VITE_CHATKIT_WORKFLOW_ID", raising=False)
    client = make_client()
    response = client.post("/api/create-session", json={})
    assert response.status_code == 400
    assert "workflow" in response.json()["error"].lower()


def test_create_session_returns_client_secret(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("CHATKIT_WORKFLOW_ID", "wf_test")

    mock_response = MagicMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"client_secret": "cs_abc123", "expires_after": 3600}

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        client = make_client()
        response = client.post("/api/create-session", json={})

    assert response.status_code == 200
    assert response.json()["client_secret"] == "cs_abc123"
