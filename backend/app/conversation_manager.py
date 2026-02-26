from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List

from google.genai import types as genai_types

from .models import ChatMessage, ChatRole


@dataclass
class ConversationState:
    conversation_id: str
    is_processing: bool = False
    pending_texts: List[str] = field(default_factory=list)


CONVERSATIONS: Dict[str, List[ChatMessage]] = {}
CONVERSATION_STATES: Dict[str, ConversationState] = {}


def get_conversation_messages(conversation_id: str) -> List[ChatMessage]:
    return CONVERSATIONS.setdefault(conversation_id, [])


def append_message(message: ChatMessage) -> None:
    messages = CONVERSATIONS.setdefault(message.conversation_id, [])
    messages.append(message)


def get_or_create_state(conversation_id: str) -> ConversationState:
    if conversation_id not in CONVERSATION_STATES:
        CONVERSATION_STATES[conversation_id] = ConversationState(conversation_id=conversation_id)
    return CONVERSATION_STATES[conversation_id]


async def process_pending_messages(
    conversation_id: str,
    runner,
    app_name: str,
) -> None:
    """
    Aggregate rapid user messages and send them to the ADK runner as a single turn.

    This function is designed to be scheduled as a background task by FastAPI.
    """
    from google.adk.sessions import InMemorySessionService  # type: ignore

    state = get_or_create_state(conversation_id)
    session_service = runner.session_service  # type: ignore[attr-defined]
    if not isinstance(session_service, InMemorySessionService):
        # For now we assume the default in-memory implementation.
        pass

    try:
        while state.pending_texts:
            # Small delay so that multiple rapid messages are grouped.
            await asyncio.sleep(0.4)

            # Take a snapshot of all pending messages.
            texts = list(state.pending_texts)
            state.pending_texts.clear()
            aggregated = "\n".join(texts)

            content = genai_types.Content(
                role="user",
                parts=[genai_types.Part(text=aggregated)],
            )

            # Ensure a session exists for this conversation.
            session_service.create_session(
                app_name=app_name,
                user_id=conversation_id,
                session_id=conversation_id,
                exists_ok=True,
            )

            events = runner.run(
                user_id=conversation_id,
                session_id=conversation_id,
                new_message=content,
            )

            for event in events:
                if event.is_final_response() and event.content:
                    text_parts = []
                    for part in event.content.parts:
                        if getattr(part, "text", None):
                            text_parts.append(part.text)
                    full_text = " ".join(text_parts).strip()
                    if full_text:
                        append_message(
                            ChatMessage(
                                id=f"assistant-{datetime.utcnow().timestamp()}",
                                conversation_id=conversation_id,
                                role=ChatRole.ASSISTANT,
                                text=full_text,
                                created_at=datetime.utcnow(),
                            )
                        )
    finally:
        state.is_processing = False

