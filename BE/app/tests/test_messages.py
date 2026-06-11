def create_chat(client, name="Messages Test Chat"):
    response = client.post(
        "/api/v1/chats",
        json={"name": name},
    )
    assert response.status_code == 201
    return response.json()


def test_list_messages_empty_for_new_chat(client):
    chat = create_chat(client)
    chat_id = chat["id"]

    response = client.get(f"/api/v1/chats/{chat_id}/messages")
    assert response.status_code == 200
    assert response.json() == []


def test_send_message_succeeds(client):
    chat = create_chat(client)
    chat_id = chat["id"]

    response = client.post(
        f"/api/v1/chats/{chat_id}/messages",
        json={"content": "Hello from pytest"},
    )

    # Keep this flexible in case your API returns 200 instead of 201
    assert response.status_code in (200, 201)

    data = response.json()
    assert data is not None


def test_messages_persist_after_send(client):
    chat = create_chat(client)
    chat_id = chat["id"]

    send_response = client.post(
        f"/api/v1/chats/{chat_id}/messages",
        json={"content": "What is this chat about?"},
    )
    assert send_response.status_code in (200, 201)

    list_response = client.get(f"/api/v1/chats/{chat_id}/messages")
    assert list_response.status_code == 200

    messages = list_response.json()
    assert isinstance(messages, list)
    assert len(messages) >= 1

    # Confirm the user message exists in history
    assert any(
        msg.get("role") == "user" and msg.get("content") == "What is this chat about?"
        for msg in messages
    )

    # If your backend also stores/generates an assistant message,
    # this verifies it without assuming exact wording.
    assistant_messages = [msg for msg in messages if msg.get("role") == "assistant"]
    if assistant_messages:
        assert all(
            isinstance(msg.get("content"), str) and msg.get("content").strip() != ""
            for msg in assistant_messages
        )


def test_get_messages_for_missing_chat_returns_404(client):
    response = client.get("/api/v1/chats/not-a-real-chat-id/messages")
    assert response.status_code == 404
    assert response.json()["detail"] == "Chat not found"


def test_send_message_to_missing_chat_returns_404(client):
    response = client.post(
        "/api/v1/chats/not-a-real-chat-id/messages",
        json={"content": "This should fail"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Chat not found"


def test_send_empty_message_fails(client):
    chat = create_chat(client)
    chat_id = chat["id"]

    response = client.post(
        f"/api/v1/chats/{chat_id}/messages",
        json={"content": ""},
    )

    # Validation could be 400 or 422 depending on how the schema/endpoint is implemented
    assert response.status_code in (400, 422)
