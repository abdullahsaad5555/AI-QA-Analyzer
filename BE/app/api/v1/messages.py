import asyncio
import json

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.core.config import settings
from app.models.users import User
from app.schemas.message import MessageCreateRequest, MessageResponse
from app.services.message_service import MessageService
from app.services.rag_service import RAGService

router = APIRouter(tags=["Messages"])


@router.get(
    "/chats/{chat_id}/messages",
    response_model=list[MessageResponse],
    status_code=status.HTTP_200_OK,
)
async def list_messages(
    chat_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> list[MessageResponse]:
    messages = await MessageService.list_chat_messages(
        db=db,
        chat_id=chat_id,
        user_id=current_user.id,
    )
    return messages


@router.post(
    "/chats/{chat_id}/messages",
    status_code=status.HTTP_200_OK,
)
async def send_message(
    request: Request,
    chat_id: str,
    payload: MessageCreateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    # 1) Save user's message first
    await MessageService.create_user_message(
        db=db,
        chat_id=chat_id,
        user_id=current_user.id,
        content=payload.content,
    )

    # 2) Small artificial delay so frontend can show thinking state
    await asyncio.sleep(1)

    # If client already disconnected, send a minimal stopped stream
    if await request.is_disconnected():
        async def disconnected_stream():
            yield json.dumps({"type": "stopped"}) + "\n"

        return StreamingResponse(
            disconnected_stream(),
            media_type="application/x-ndjson",
        )

    async def event_stream():
        # Static/dev mode path
        if settings.ENABLE_STATIC_CHAT_RESPONSES:
            assistant_text = (
                f"{settings.STATIC_CHAT_RESPONSE_TEXT}\n\n"
                f"Question received: {payload.content}"
            )
            sources = []

            chunk_size = 40
            for start in range(0, len(assistant_text), chunk_size):
                if await request.is_disconnected():
                    yield json.dumps({"type": "stopped"}) + "\n"
                    return

                delta = assistant_text[start:start + chunk_size]

                yield json.dumps(
                    {
                        "type": "chunk",
                        "delta": delta,
                    }
                ) + "\n"

                await asyncio.sleep(0.03)

            await MessageService.create_assistant_message(
                db=db,
                chat_id=chat_id,
                user_id=current_user.id,
                content=assistant_text,
            )

            yield json.dumps(
                {
                    "type": "done",
                    "answer": assistant_text,
                    "sources": sources,
                }
            ) + "\n"
            return

        # RAG streaming-friendly path
        assistant_text = ""
        sources = []

        async for event in RAGService.stream_answer_question(
            db=db,
            chat_id=chat_id,
            user_id=current_user.id,
            question=payload.content,
            top_k=5,
        ):
            if await request.is_disconnected():
                yield json.dumps({"type": "stopped"}) + "\n"
                return

            if event["type"] == "chunk":
                assistant_text += event["delta"]
                yield json.dumps(event) + "\n"
                await asyncio.sleep(0.03)

            elif event["type"] == "done":
                sources = event["sources"]

                await MessageService.create_assistant_message(
                    db=db,
                    chat_id=chat_id,
                    user_id=current_user.id,
                    content=assistant_text,
                )

                yield json.dumps(
                    {
                        "type": "done",
                        "answer": assistant_text,
                        "sources": sources,
                    }
                ) + "\n"
                return

    return StreamingResponse(
        event_stream(),
        media_type="application/x-ndjson",
    )