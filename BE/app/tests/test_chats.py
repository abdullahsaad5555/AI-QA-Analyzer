def test_list_chats_empty(client):
    response = client.get("/api/v1/chats")
    assert response.status_code == 200
    assert response.json() == []


def test_create_chat(client):
    response = client.post(
        "/api/v1/chats",
        json={"name": "Smoke Test Chat"},
    )

    assert response.status_code == 201
    data = response.json()

    assert data["name"] == "Smoke Test Chat"
    assert "id" in data
    assert isinstance(data["id"], str)
    assert data["id"] != ""


def test_list_chats_after_create(client):
    create_response = client.post(
        "/api/v1/chats",
        json={"name": "My First Chat"},
    )
    assert create_response.status_code == 201

    list_response = client.get("/api/v1/chats")
    assert list_response.status_code == 200

    data = list_response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "My First Chat"


def test_get_chat_by_id(client):
    create_response = client.post(
        "/api/v1/chats",
        json={"name": "Open Me"},
    )
    assert create_response.status_code == 201

    created = create_response.json()
    chat_id = created["id"]

    get_response = client.get(f"/api/v1/chats/{chat_id}")
    assert get_response.status_code == 200

    data = get_response.json()
    assert data["id"] == chat_id
    assert data["name"] == "Open Me"


def test_update_chat_name(client):
    create_response = client.post(
        "/api/v1/chats",
        json={"name": "Old Name"},
    )
    assert create_response.status_code == 201

    created = create_response.json()
    chat_id = created["id"]

    patch_response = client.patch(
        f"/api/v1/chats/{chat_id}",
        json={"name": "New Name"},
    )
    assert patch_response.status_code == 200

    updated = patch_response.json()
    assert updated["id"] == chat_id
    assert updated["name"] == "New Name"


def test_delete_chat(client):
    create_response = client.post(
        "/api/v1/chats",
        json={"name": "Delete Me"},
    )
    assert create_response.status_code == 201

    created = create_response.json()
    chat_id = created["id"]

    delete_response = client.delete(f"/api/v1/chats/{chat_id}")
    assert delete_response.status_code == 204

    list_response = client.get("/api/v1/chats")
    assert list_response.status_code == 200
    assert list_response.json() == []


def test_get_missing_chat_returns_404(client):
    response = client.get("/api/v1/chats/not-a-real-chat-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Chat not found"