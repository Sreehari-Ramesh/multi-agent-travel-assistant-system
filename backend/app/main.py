from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import BackgroundTasks, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .agents import build_agents
from .config import get_settings
from .conversation_manager import (
    append_message,
    get_conversation_messages,
    get_or_create_state,
    process_pending_messages,
)
from .mock_db import list_activities
from .models import ChatMessage, ChatMessageCreate, ChatMessageResponse, ChatRole


settings = get_settings()
root_agent, runner = build_agents()

app = FastAPI(title=settings.app_name)

if settings.frontend_origin:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get(f"{settings.api_prefix}/activities", tags=["activities"])
def list_all_activities() -> list[dict[str, Any]]:
    return [a.dict() for a in list_activities()]


@app.get(f"{settings.api_prefix}/chat/{{conversation_id}}", response_model=ChatMessageResponse, tags=["chat"])
def get_chat(conversation_id: str) -> ChatMessageResponse:
    messages = get_conversation_messages(conversation_id)
    return ChatMessageResponse(messages=messages)


@app.post(f"{settings.api_prefix}/chat/{{conversation_id}}", response_model=ChatMessage, tags=["chat"])
async def post_chat_message(
    conversation_id: str,
    payload: ChatMessageCreate,
    background_tasks: BackgroundTasks,
) -> ChatMessage:
    # Store user message
    msg = ChatMessage(
        id=f"user-{datetime.utcnow().timestamp()}",
        conversation_id=conversation_id,
        role=ChatRole.USER,
        text=payload.text,
        created_at=datetime.utcnow(),
    )
    append_message(msg)

    # Queue processing by the multi-agent system
    state = get_or_create_state(conversation_id)
    state.pending_texts.append(payload.text)
    if not state.is_processing:
        state.is_processing = True
        background_tasks.add_task(
            process_pending_messages,
            conversation_id=conversation_id,
            runner=runner,
            app_name=settings.app_name,
        )

    return msg


@app.post(
    f"{settings.api_prefix}/escalations/{{conversation_id}}/supervisor-reply",
    tags=["human-in-the-loop"],
)
async def supervisor_reply(
    conversation_id: str,
    body: dict[str, str],
) -> dict[str, str]:
    """
    Endpoint to simulate a supervisor replying to an escalation email.

    In a real deployment, this would be called by an email webhook. Here we
    simply inject the supervisor's message into the chat history so the
    frontend can display it seamlessly.
    """
    message = body.get("message", "").strip()
    if not message:
        return {"status": "ignored", "reason": "empty message"}

    supervisor_msg = ChatMessage(
        id=f"supervisor-{datetime.utcnow().timestamp()}",
        conversation_id=conversation_id,
        role=ChatRole.SUPERVISOR,
        text=message,
        created_at=datetime.utcnow(),
    )
    append_message(supervisor_msg)
    return {"status": "ok"}

