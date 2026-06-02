# app/api/v1/__init__.py

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.chats import router as chats_router
from app.api.v1.documents import router as documents_router
from app.api.v1.messages import router as messages_router


api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(chats_router)
api_router.include_router(documents_router)

api_router.include_router(messages_router)
