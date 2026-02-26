from __future__ import annotations

from typing import List, Optional

from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm  # For multi-model support
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.agent_tool import AgentTool
from google.genai import types as genai_types

from .config import get_settings
from .email_service import send_escalation_email
from .mock_db import (
    list_activities,
    get_activity,
    create_booking,
    create_escalation,
)
from .models import BookingStatus


def search_activities_tool(query: str) -> dict:
    """Search available Dubai activities by name or description."""
    activities = list_activities()
    q = query.lower()
    results = [
        a.dict()
        for a in activities
        if q in a.name.lower() or q in a.description.lower()
    ]
    return {"status": "success", "results": results}


def get_activity_details_tool(activity_id: str) -> dict:
    """Return full details, images, and policies for a specific activity."""
    activity = get_activity(activity_id)
    if not activity:
        return {"status": "error", "error_message": "Activity not found."}
    return {"status": "success", "activity": activity.dict()}


def get_pricing_for_variation_tool(activity_id: str, variation_id: str) -> dict:
    """Return pricing and capacity for a specific activity variation."""
    activity = get_activity(activity_id)
    if not activity:
        return {"status": "error", "error_message": "Activity not found."}
    variation = next((v for v in activity.variations if v.id == variation_id), None)
    if not variation:
        return {"status": "error", "error_message": "Variation not found."}
    return {
        "status": "success",
        "activity_id": activity_id,
        "variation": variation.dict(),
    }


def book_activity_tool(
    activity_id: str,
    variation_id: str,
    customer_name: str,
    customer_email: str,
    group_size: int,
    date: str,
) -> dict:
    """Attempt to create a booking for a given activity and variation.

    If the requested variation is unavailable or group size is out of range,
    the tool will create a pending booking, trigger escalation to a human
    supervisor via email, and return a 'pending_supervisor' status.
    """
    settings = get_settings()
    activity = get_activity(activity_id)
    if not activity:
        return {"status": "error", "error_message": "Activity not found."}

    variation = next((v for v in activity.variations if v.id == variation_id), None)
    if not variation:
        return {"status": "error", "error_message": "Variation not found."}

    needs_escalation = False
    reason_parts: List[str] = []

    if not variation.is_available:
        needs_escalation = True
        reason_parts.append("Requested variation is currently unavailable.")

    if group_size < variation.group_size_min or group_size > variation.group_size_max:
        needs_escalation = True
        reason_parts.append(
            f"Requested group size {group_size} is outside allowed range "
            f"{variation.group_size_min}-{variation.group_size_max}."
        )

    if needs_escalation:
        booking = create_booking(
            activity_id=activity_id,
            variation_id=variation_id,
            customer_name=customer_name,
            customer_email=customer_email,
            group_size=group_size,
            date=date,
            status=BookingStatus.PENDING_SUPERVISOR,
        )

        reason = " ".join(reason_parts) or "Supervisor approval required."
        escalation = create_escalation(
            booking=booking,
            reason=reason,
            supervisor_email=settings.supervisor_email or "unknown@local",
        )

        subject = f"[Dubai Travel Assistant] Escalation for booking {booking.id}"
        body = (
            f"A booking requires your attention.\n\n"
            f"Booking ID: {booking.id}\n"
            f"Activity: {activity.name}\n"
            f"Variation: {variation.name}\n"
            f"Requested date: {date}\n"
            f"Group size: {group_size}\n"
            f"Customer: {customer_name} <{customer_email}>\n\n"
            f"Reason for escalation: {reason}\n\n"
            f"Please reply with APPROVE or REJECT and any notes. "
            f"Your response will be surfaced to the user in the chat."
        )
        send_escalation_email(subject=subject, body=body, to_email=escalation.supervisor_email)

        return {
            "status": "pending_supervisor",
            "booking": booking.dict(),
            "escalation_id": escalation.id,
            "message": (
                "Your request requires manual review by our supervisor. "
                "We have sent an escalation and will update you once they respond."
            ),
        }

    booking = create_booking(
        activity_id=activity_id,
        variation_id=variation_id,
        customer_name=customer_name,
        customer_email=customer_email,
        group_size=group_size,
        date=date,
        status=BookingStatus.CONFIRMED,
    )
    return {
        "status": "confirmed",
        "booking": booking.dict(),
        "message": "Your activity has been booked successfully.",
    }


def build_agents() -> tuple[LlmAgent, Runner]:
    """Construct the information, booking, and conversation handler agents and runner."""
    settings = get_settings()

    # Information agent - focuses on images, policies, and pricing.
    information_agent = Agent(
        model=LiteLlm(model=settings.adk_model),
        name="information_agent",
        description="Provides Dubai activity information, images, policies, and pricing.",
        instruction=(
            "You are an information specialist for Dubai attractions. "
            "Use tools to fetch images, cancellation and reschedule policies, and pricing for "
            "different activity variations. Always respond clearly and concisely."
        ),
        tools=[
            search_activities_tool,
            get_activity_details_tool,
            get_pricing_for_variation_tool,
        ],
    )

    # Booking agent - focuses on creating bookings and handling unavailability.
    booking_agent = Agent(
        model=LiteLlm(model=settings.adk_model),
        name="booking_agent",
        description="Handles booking requests for Dubai activities, including variations and group sizes.",
        instruction=(
            "You are a booking specialist. "
            "When a user wants to book an activity, collect the required details like activity name, "
            "chosen variation, date, group size, and contact info, then call the booking tool. "
            "If the tool reports a supervisor review is needed, explain this clearly to the user."
        ),
        tools=[
            search_activities_tool,
            get_activity_details_tool,
            get_pricing_for_variation_tool,
            book_activity_tool,
        ],
    )

    # Conversation handler / root agent.
    root_agent = LlmAgent(
        model=LiteLlm(model=settings.adk_model),
        name="conversation_handler",
        description=(
            "WhatsApp-style travel assistant for booking and learning about Dubai activities. "
            "Understands multi-turn conversations and message interruptions."
        ),
        instruction=(
            "You are a friendly WhatsApp-style travel assistant focused on Dubai activities. "
            "You can do two main things:\n"
            "1) Provide information (images, pricing, policies) about activities.\n"
            "2) Help the user book activities, including handling different time slots and group sizes.\n\n"
            "Guidelines:\n"
            "- If the user is asking general questions or wants to compare options, use the information tools.\n"
            "- If the user clearly wants to book or reserve, use the booking tools.\n"
            "- The user may send several short messages in a row; treat them as a single request.\n"
            "- Always confirm details back to the user in natural language.\n"
            "- When a booking goes to supervisor review, explain that they will see their reply in this chat."
        ),
        tools=[
            AgentTool(agent=information_agent),
            AgentTool(agent=booking_agent),
            search_activities_tool,
            get_activity_details_tool,
            get_pricing_for_variation_tool,
            book_activity_tool,
        ],
    )

    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name=settings.app_name,
        session_service=session_service,
    )
    return root_agent, runner


def build_user_message(text: str) -> genai_types.Content:
    return genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=text)],
    )

