from __future__ import annotations

from typing import Dict, List

from .models import Activity, ActivityVariation, Booking, BookingStatus, Escalation
from datetime import datetime
import uuid


# In-memory "database" for activities, bookings, and escalations.
ACTIVITIES: Dict[str, Activity] = {}
BOOKINGS: Dict[str, Booking] = {}
ESCALATIONS: Dict[str, Escalation] = {}


def _seed_activities() -> None:
    """Populate the in-memory activities store with sample Dubai activities."""
    global ACTIVITIES
    if ACTIVITIES:
        return

    activities: List[Activity] = [
        Activity(
            id="burj-khalifa-observation",
            name="Burj Khalifa At The Top - Observation Deck",
            description="Skip-the-line access to Burj Khalifa's observation deck with stunning city views.",
            images=[
                "https://cdn.pixabay.com/photo/2013/04/21/14/49/dubai-106202_1280.jpg",
            ],
            variations=[
                ActivityVariation(
                    id="prime-hours-small-group",
                    name="Prime Hours (Sunset) - Small Group",
                    time_slot="16:00-19:00",
                    group_size_min=1,
                    group_size_max=6,
                    price_per_person=320.0,
                ),
                ActivityVariation(
                    id="non-prime-standard",
                    name="Non-Prime Hours - Standard",
                    time_slot="10:00-15:00",
                    group_size_min=1,
                    group_size_max=10,
                    price_per_person=210.0,
                ),
            ],
            cancellation_policy="Full refund up to 48 hours before visit. No refund within 48 hours.",
            reschedule_policy="Free reschedule up to 24 hours before visit, subject to availability.",
        ),
        Activity(
            id="desert-safari",
            name="Premium Desert Safari with BBQ Dinner",
            description="Evening desert safari with dune bashing, camel ride, live shows, and BBQ dinner.",
            images=[
                "https://www.desertsafaridubai.com/img/portfolio/1.jpg",
                "https://www.desertsafaridubai.com/img/portfolio/2.jpg",
            ],
            variations=[
                ActivityVariation(
                    id="safari-shared-4x4",
                    name="Shared 4x4 Vehicle",
                    time_slot="15:00-22:00",
                    group_size_min=1,
                    group_size_max=6,
                    price_per_person=280.0,
                ),
                ActivityVariation(
                    id="safari-private-4x4",
                    name="Private 4x4 Vehicle",
                    time_slot="15:00-22:00",
                    group_size_min=2,
                    group_size_max=6,
                    price_per_person=450.0,
                ),
            ],
            cancellation_policy="Full refund up to 24 hours before experience.",
            reschedule_policy="One free reschedule up to 12 hours before pick-up.",
        ),
        Activity(
            id="dubai-marina-cruise",
            name="Dubai Marina Dhow Cruise with Dinner",
            description="Relaxing dhow cruise along Dubai Marina with buffet dinner and soft drinks.",
            images=[
                "https://cdn.pixabay.com/photo/2013/12/17/23/31/dubai-230075_1280.jpg",
            ],
            variations=[
                ActivityVariation(
                    id="cruise-upper-deck",
                    name="Upper Deck - Open Air",
                    time_slot="20:00-22:00",
                    group_size_min=1,
                    group_size_max=8,
                    price_per_person=220.0,
                ),
                ActivityVariation(
                    id="cruise-lower-deck",
                    name="Lower Deck - AC",
                    time_slot="20:00-22:00",
                    group_size_min=1,
                    group_size_max=10,
                    price_per_person=190.0,
                ),
            ],
            cancellation_policy="Full refund up to 24 hours before cruise.",
            reschedule_policy="Free reschedule up to 6 hours before boarding.",
        ),
        Activity(
            id="dubai-frame",
            name="Dubai Frame Entry Ticket",
            description="Visit Dubai Frame and enjoy panoramic views of old and new Dubai.",
            images=[
                "https://cdn.pixabay.com/photo/2021/07/23/07/51/dubai-6486776_1280.jpg",
            ],
            variations=[
                ActivityVariation(
                    id="frame-standard",
                    name="Standard Entry",
                    time_slot="09:00-21:00",
                    group_size_min=1,
                    group_size_max=15,
                    price_per_person=75.0,
                ),
            ],
            cancellation_policy="Full refund up to 24 hours before visit.",
            reschedule_policy="Free reschedule up to 12 hours before entry.",
        ),
        Activity(
            id="global-village",
            name="Global Village Entry with Transfers",
            description="Evening visit to Global Village with optional transfer from Dubai hotels.",
            images=[
                "https://cdn.pixabay.com/photo/2015/03/18/15/00/global-village-679413_1280.jpg",
            ],
            variations=[
                ActivityVariation(
                    id="gv-entry-only",
                    name="Entry Ticket Only",
                    time_slot="16:00-23:00",
                    group_size_min=1,
                    group_size_max=20,
                    price_per_person=30.0,
                ),
                ActivityVariation(
                    id="gv-entry-transfer",
                    name="Entry + Shared Transfers",
                    time_slot="16:00-23:00",
                    group_size_min=2,
                    group_size_max=10,
                    price_per_person=120.0,
                ),
            ],
            cancellation_policy="Non-refundable once booked.",
            reschedule_policy="No reschedule available.",
        ),
        Activity(
            id="aquaventure",
            name="Aquaventure Waterpark at Atlantis",
            description="Full-day access to Aquaventure Waterpark with record-breaking slides.",
            images=[
                "https://cdn.pixabay.com/photo/2015/09/14/14/37/aquaventure-939646_1280.jpg",
            ],
            variations=[
                ActivityVariation(
                    id="aquaventure-standard",
                    name="Standard Full-Day Access",
                    time_slot="10:00-18:00",
                    group_size_min=1,
                    group_size_max=10,
                    price_per_person=350.0,
                ),
            ],
            cancellation_policy="Full refund up to 48 hours before date.",
            reschedule_policy="One free reschedule up to 24 hours before visit.",
        ),
        Activity(
            id="skydiving-palm",
            name="Tandem Skydive over The Palm",
            description="Bucket-list tandem skydive with views over Palm Jumeirah.",
            images=[
                "https://cdn.pixabay.com/photo/2017/09/05/12/52/skydive-2717507_1280.jpg",
            ],
            variations=[
                ActivityVariation(
                    id="skydiving-morning",
                    name="Morning Slot",
                    time_slot="08:00-11:00",
                    group_size_min=1,
                    group_size_max=4,
                    price_per_person=2200.0,
                ),
                ActivityVariation(
                    id="skydiving-afternoon",
                    name="Afternoon Slot",
                    time_slot="12:00-15:00",
                    group_size_min=1,
                    group_size_max=4,
                    price_per_person=2200.0,
                    is_available=False,
                ),
            ],
            cancellation_policy=(
                "Strict weather and safety dependent. Refunds/reschedules as per operator policy."
            ),
            reschedule_policy="Reschedules allowed only if operator cancels due to weather.",
        ),
        Activity(
            id="miracle-garden",
            name="Dubai Miracle Garden Entry",
            description="Access to the world's largest natural flower garden.",
            images=[
                "https://cdn.pixabay.com/photo/2018/09/18/13/29/miracle-garden-dubai-3686191_1280.jpg",
            ],
            variations=[
                ActivityVariation(
                    id="miracle-standard",
                    name="Standard Entry",
                    time_slot="09:00-21:00",
                    group_size_min=1,
                    group_size_max=15,
                    price_per_person=85.0,
                ),
            ],
            cancellation_policy="Full refund up to 24 hours before visit.",
            reschedule_policy="Free reschedule up to 12 hours before entry.",
        ),
        Activity(
            id="dolphinarium",
            name="Dubai Dolphinarium Dolphin & Seal Show",
            description="Family-friendly dolphin and seal show with optional VIP seating.",
            images=[
                "https://cdn.pixabay.com/photo/2016/01/11/01/46/dolphins-1132847_1280.jpg",
            ],
            variations=[
                ActivityVariation(
                    id="dolphin-regular",
                    name="Regular Seat",
                    time_slot="11:00-12:00",
                    group_size_min=1,
                    group_size_max=15,
                    price_per_person=110.0,
                ),
                ActivityVariation(
                    id="dolphin-vip",
                    name="VIP Seat",
                    time_slot="15:00-16:00",
                    group_size_min=1,
                    group_size_max=10,
                    price_per_person=175.0,
                ),
            ],
            cancellation_policy="Full refund up to 24 hours before show.",
            reschedule_policy="Free reschedule up to 6 hours before show time.",
        ),
        Activity(
            id="la-perle-show",
            name="La Perle by Dragone Show",
            description="Spectacular aqua theater show with gravity-defying stunts.",
            images=[
                "https://cdn.pixabay.com/photo/2023/08/24/00/58/horse-8209523_1280.jpg",
            ],
            variations=[
                ActivityVariation(
                    id="la-perle-silver",
                    name="Silver Ticket",
                    time_slot="19:00-20:30",
                    group_size_min=1,
                    group_size_max=10,
                    price_per_person=350.0,
                ),
                ActivityVariation(
                    id="la-perle-gold",
                    name="Gold Ticket",
                    time_slot="21:00-22:30",
                    group_size_min=1,
                    group_size_max=8,
                    price_per_person=480.0,
                ),
            ],
            cancellation_policy="Full refund up to 48 hours before show.",
            reschedule_policy="Free reschedule up to 24 hours before show.",
        ),
    ]

    ACTIVITIES = {activity.id: activity for activity in activities}


def list_activities() -> List[Activity]:
    _seed_activities()
    return list(ACTIVITIES.values())


def get_activity(activity_id: str) -> Activity | None:
    _seed_activities()
    return ACTIVITIES.get(activity_id)


def create_booking(
    activity_id: str,
    variation_id: str,
    customer_name: str,
    customer_email: str,
    group_size: int,
    date: str,
    status: BookingStatus,
) -> Booking:
    booking_id = str(uuid.uuid4())
    booking = Booking(
        id=booking_id,
        activity_id=activity_id,
        variation_id=variation_id,
        customer_name=customer_name,
        customer_email=customer_email,
        group_size=group_size,
        date=date,
        status=status,
        created_at=datetime.utcnow(),
    )
    BOOKINGS[booking_id] = booking
    return booking


def create_escalation(booking: Booking, reason: str, supervisor_email: str) -> Escalation:
    escalation_id = str(uuid.uuid4())
    escalation = Escalation(
        id=escalation_id,
        booking_id=booking.id,
        reason=reason,
        supervisor_email=supervisor_email,
        created_at=datetime.utcnow(),
    )
    ESCALATIONS[escalation_id] = escalation
    return escalation

