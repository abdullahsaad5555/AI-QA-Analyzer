def create_chat(client, name="Documents Test Chat"):
    response = client.post(
        "/api/v1/chats",
        json={"name": name},
    )
    assert response.status_code == 201
    return response.json()


def create_text_document(
    client,
    chat_id,
    file_name="notes.txt",
    raw_text="Hello from pytest",
):
    response = client.post(
        f"/api/v1/chats/{chat_id}/documents/text",
        json={
            "file_name": file_name,
            "raw_text": raw_text,
        },
    )
    assert response.status_code in (200, 201)
    return response.json()


def test_list_documents_empty_for_new_chat(client):
    chat = create_chat(client)
    chat_id = chat["id"]

    response = client.get(f"/api/v1/chats/{chat_id}/documents")
    assert response.status_code == 200
    assert response.json() == []


def test_create_text_document(client):
    chat = create_chat(client)
    chat_id = chat["id"]

    response = client.post(
        f"/api/v1/chats/{chat_id}/documents/text",
        json={
            "file_name": "smoke-test.txt",
            "raw_text": "This is a document created by pytest.",
        },
    )

    assert response.status_code in (200, 201)
    data = response.json()

    assert "id" in data
    assert isinstance(data["id"], str)
    assert data["id"] != ""

    if "file_name" in data:
        assert data["file_name"] == "smoke-test.txt"


def test_list_documents_after_text_create(client):
    chat = create_chat(client)
    chat_id = chat["id"]

    created = create_text_document(
        client,
        chat_id,
        file_name="notes.txt",
        raw_text="Persistent text content",
    )

    response = client.get(f"/api/v1/chats/{chat_id}/documents")
    assert response.status_code == 200

    docs = response.json()
    assert isinstance(docs, list)
    assert len(docs) == 1

    assert docs[0]["id"] == created["id"]
    if "file_name" in docs[0]:
        assert docs[0]["file_name"] == "notes.txt"


def test_upload_document(client):
    chat = create_chat(client)
    chat_id = chat["id"]

    response = client.post(
        f"/api/v1/chats/{chat_id}/documents/upload",
        files={
            "file": (
                "smoke-upload.txt",
                b"hello from uploaded pytest file",
                "text/plain",
            )
        },
    )

    assert response.status_code in (200, 201)
    data = response.json()

    assert "id" in data
    assert isinstance(data["id"], str)
    assert data["id"] != ""

    if "file_name" in data:
        assert data["file_name"] == "smoke-upload.txt"


def test_get_document_by_id(client):
    chat = create_chat(client)
    chat_id = chat["id"]

    created = create_text_document(
        client,
        chat_id,
        file_name="get-me.txt",
        raw_text="Fetch me by ID",
    )

    document_id = created["id"]

    response = client.get(f"/api/v1/documents/{document_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == document_id

    if "file_name" in data:
        assert data["file_name"] == "get-me.txt"


def test_ingest_document(client):
    chat = create_chat(client)
    chat_id = chat["id"]

    created = create_text_document(
        client,
        chat_id,
        file_name="ingest-me.txt",
        raw_text="Please ingest this document.",
    )

    document_id = created["id"]

    response = client.post(f"/api/v1/documents/{document_id}/ingest")
    assert response.status_code in (200, 202)

    data = response.json()
    assert data is not None


def test_delete_document(client):
    chat = create_chat(client)
    chat_id = chat["id"]

    created = create_text_document(
        client,
        chat_id,
        file_name="delete-me.txt",
        raw_text="Please delete this document.",
    )

    document_id = created["id"]

    delete_response = client.delete(f"/api/v1/documents/{document_id}")
    assert delete_response.status_code in (200, 204)

    list_response = client.get(f"/api/v1/chats/{chat_id}/documents")
    assert list_response.status_code == 200

    docs = list_response.json()
    assert isinstance(docs, list)
    assert all(doc["id"] != document_id for doc in docs)


def test_list_documents_for_missing_chat_returns_404(client):
    response = client.get("/api/v1/chats/not-a-real-chat-id/documents")
    assert response.status_code == 404


def test_create_text_document_for_missing_chat_returns_404(client):
    response = client.post(
        "/api/v1/chats/not-a-real-chat-id/documents/text",
        json={
            "file_name": "ghost.txt",
            "raw_text": "This should fail",
        },
    )
    assert response.status_code == 404


def test_upload_document_for_missing_chat_returns_404(client):
    response = client.post(
        "/api/v1/chats/not-a-real-chat-id/documents/upload",
        files={
            "file": ("ghost.txt", b"this should fail", "text/plain")
        },
    )
    assert response.status_code == 404


def test_ingest_missing_document_returns_404(client):
    response = client.post("/api/v1/documents/not-a-real-document-id/ingest")
    assert response.status_code == 404


def test_delete_missing_document_returns_404(client):
    response = client.delete("/api/v1/documents/not-a-real-document-id")
    assert response.status_code == 404
