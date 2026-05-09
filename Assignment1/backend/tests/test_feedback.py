from pathlib import Path
import backend.app.routers.feedback as feedback_module


def make_client():
    from backend.app.main import app
    from fastapi.testclient import TestClient
    return TestClient(app)


def test_submit_feedback_returns_201(tmp_path, monkeypatch):
    monkeypatch.setattr(feedback_module, "DATA_FILE", tmp_path / "feedback.json")
    client = make_client()
    response = client.post(
        "/api/feedback",
        json={"project": "chatkit-agent", "comment": "Great project!", "rating": 5},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["ok"] is True
    assert isinstance(data["id"], int)


def test_submit_feedback_persists(tmp_path, monkeypatch):
    monkeypatch.setattr(feedback_module, "DATA_FILE", tmp_path / "feedback.json")
    client = make_client()
    client.post("/api/feedback", json={"project": "chatkit-agent", "comment": "Nice!"})
    response = client.get("/api/admin/feedback")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["feedback"][0]["comment"] == "Nice!"


def test_filter_by_project(tmp_path, monkeypatch):
    monkeypatch.setattr(feedback_module, "DATA_FILE", tmp_path / "feedback.json")
    client = make_client()
    client.post("/api/feedback", json={"project": "chatkit-agent", "comment": "Agent comment"})
    client.post("/api/feedback", json={"project": "other-project", "comment": "Other comment"})
    response = client.get("/api/admin/feedback?project=chatkit-agent")
    body = response.json()
    assert body["total"] == 1
    assert body["feedback"][0]["project"] == "chatkit-agent"


def test_comment_required(tmp_path, monkeypatch):
    monkeypatch.setattr(feedback_module, "DATA_FILE", tmp_path / "feedback.json")
    client = make_client()
    response = client.post("/api/feedback", json={"project": "chatkit-agent", "comment": ""})
    assert response.status_code == 422


def test_rating_optional(tmp_path, monkeypatch):
    monkeypatch.setattr(feedback_module, "DATA_FILE", tmp_path / "feedback.json")
    client = make_client()
    response = client.post(
        "/api/feedback",
        json={"project": "chatkit-agent", "comment": "No rating here"},
    )
    assert response.status_code == 201
    assert response.json()["ok"] is True
