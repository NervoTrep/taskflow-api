"""Tests cover the public HTTP API, not internal implementation details."""

from fastapi.testclient import TestClient


def create_task(client: TestClient, title: str = "Read docs", **kwargs):
    return client.post("/api/v1/tasks", json={"title": title, **kwargs})


def test_health(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_task_with_defaults(client: TestClient):
    response = create_task(client)
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["title"] == "Read docs"
    assert body["status"] == "todo"
    assert body["priority"] == "medium"
    assert body["created_at"]


def test_create_task_with_all_fields(client: TestClient):
    response = create_task(
        client,
        title="Implement API",
        description="Add endpoints and tests",
        status="in_progress",
        priority="high",
        due_date="2027-01-15",
    )
    assert response.status_code == 201
    assert response.json()["due_date"] == "2027-01-15"
    assert response.json()["status"] == "in_progress"


def test_get_task(client: TestClient):
    task_id = create_task(client).json()["id"]
    response = client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_get_missing_task(client: TestClient):
    response = client.get("/api/v1/tasks/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_list_tasks_pagination(client: TestClient):
    for number in range(3):
        create_task(client, title=f"Task {number}")
    response = client.get("/api/v1/tasks", params={"offset": 1, "limit": 1})
    assert response.status_code == 200
    assert response.json()["total"] == 3
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["title"] == "Task 1"


def test_list_tasks_filters_and_search(client: TestClient):
    create_task(client, title="Write documentation", status="done", priority="high")
    create_task(client, title="Write tests", status="todo", priority="low")
    create_task(client, title="Buy groceries", status="done", priority="low")
    response = client.get(
        "/api/v1/tasks", params={"status": "done", "priority": "high", "search": "write"}
    )
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["title"] == "Write documentation"


def test_update_task(client: TestClient):
    task_id = create_task(client).json()["id"]
    response = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"title": "Finish project", "status": "done", "priority": "high"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Finish project"
    assert response.json()["status"] == "done"
    assert response.json()["priority"] == "high"


def test_update_nullable_fields(client: TestClient):
    task_id = create_task(client, description="Temporary").json()["id"]
    response = client.patch(f"/api/v1/tasks/{task_id}", json={"description": None})
    assert response.status_code == 200
    assert response.json()["description"] is None


def test_update_missing_task(client: TestClient):
    response = client.patch("/api/v1/tasks/999", json={"status": "done"})
    assert response.status_code == 404


def test_delete_task(client: TestClient):
    task_id = create_task(client).json()["id"]
    response = client.delete(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 204
    assert client.get(f"/api/v1/tasks/{task_id}").status_code == 404


def test_delete_missing_task(client: TestClient):
    assert client.delete("/api/v1/tasks/999").status_code == 404


def test_reject_empty_title(client: TestClient):
    response = create_task(client, title="   ")
    assert response.status_code == 422


def test_reject_invalid_status(client: TestClient):
    assert create_task(client, status="unknown").status_code == 422


def test_reject_null_title_on_update(client: TestClient):
    task_id = create_task(client).json()["id"]
    response = client.patch(f"/api/v1/tasks/{task_id}", json={"title": None})
    assert response.status_code == 422


def test_invalid_pagination(client: TestClient):
    assert client.get("/api/v1/tasks", params={"limit": 101}).status_code == 422


def test_stats(client: TestClient):
    create_task(client, title="A", status="done")
    create_task(client, title="B", status="done")
    create_task(client, title="C", status="todo")
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    assert response.json() == {
        "total": 3,
        "by_status": {"todo": 1, "in_progress": 0, "done": 2},
    }
