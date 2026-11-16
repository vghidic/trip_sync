from collections import defaultdict
from decimal import Decimal
import hashlib
import secrets

from django.shortcuts import get_object_or_404

from trips.models import ReadOnlyShareLink, Trip, TripInvitation


def money(value, currency):
    return f'{value:,.2f} {currency}'.replace('.00 ', ' ')


def short_date(value):
    return f'{value:%b} {value.day}'


def trip_for_slug(slug):
    return get_object_or_404(
        Trip.objects.prefetch_related('participants', 'destinations'),
        slug=slug,
    )


def trip_context(trip):
    destination = trip.final_destination
    participants = list(trip.participants.all())
    return {
        'slug': trip.slug,
        'name': trip.name,
        'destination': destination.city if destination else 'Destination pending',
        'country': destination.country if destination else '',
        'tagline': trip.description,
        'dates': f'{short_date(trip.departure_date)}–{trip.return_date.day}',
        'dates_long': (
            f'{short_date(trip.departure_date)}–{trip.return_date.day}, '
            f'{trip.return_date.year}'
        ),
        'dates_note': f'{(trip.return_date - trip.departure_date).days} nights',
        'countdown': '',
        # The budget is set per person (total / expected group size), so show
        # that: multiplying by who has joined so far would understate it.
        'budget': f'{money(trip.budget_per_person, trip.currency)} / person',
        'budget_note': (
            f'{money(trip.total_budget, trip.currency)} for the '
            f'{len(participants)} '
            f'{"person" if len(participants) == 1 else "people"} in so far'
        ),
        'decisions_settled': (
            trip.destinations.filter(status='approved').count()
            + trip.accommodation_proposals.filter(status='approved').count()
            + trip.transfer_proposals.filter(status='approved').count()
            + int(trip.final_destination_id is not None)
        ),
        'decisions_total': (
            trip.destinations.count()
            + trip.accommodation_proposals.count()
            + trip.transfer_proposals.count()
            + 1
        ),
        'photo': destination.city.lower() if destination else 'default',
        'friends': [
            {
                'name': user.get_full_name() or user.username,
                'initials': ''.join(
                    part[0] for part in (user.first_name, user.last_name) if part
                ).upper()[:2],
                'is_me': False,
            }
            for user in participants
        ],
    }


def user_initials(user):
    initials = ''.join(
        part[0] for part in (user.first_name, user.last_name) if part
    ).upper()[:2]
    return initials or user.get_username()[:1].upper()


def user_context(user):
    return {
        'name': user.get_full_name() or user.username,
        'initials': user_initials(user),
    }


def itinerary_context(trip):
    itinerary = trip.final_destination.itinerary
    entries_by_day = defaultdict(list)
    for item in itinerary.items.select_related('activity'):
        entries_by_day[item.start_at.date()].append({
            'time': item.start_at.strftime('%H:%M'),
            'title': item.activity.name,
            'place': item.activity.description,
            'meta': (
                f'{item.duration_minutes} minutes · '
                f'{money(item.activity.estimated_cost, trip.currency)}'
            ),
            'icon': 'pin',
        })

    ordered_days = sorted(entries_by_day.items())
    days = [
        {
            'num': day.day,
            'weekday': day.strftime('%a'),
            'note': f'{len(entries)} plans',
            'active': index == 0,
        }
        for index, (day, entries) in enumerate(ordered_days)
    ]
    first_day, first_entries = ordered_days[0]
    return {
        'eyebrow': f'{trip.final_destination.city} · {short_date(first_day)}',
        'title': 'The agreed itinerary.',
        'lede': 'Activities selected for the final destination.',
        'days': days,
        'day_title': first_day.strftime('%A, %B ') + str(first_day.day),
        'day_status': 'Approved' if itinerary.approved_at else 'Draft',
        'entries': first_entries,
        'gap_label': 'Time between plans',
        'nudge': {
            'title': 'Final destination selected',
            'note': trip.final_destination.city,
        },
    }


def money_context(trip):
    expenses = list(
        trip.expenses.select_related('paid_by').prefetch_related('shares__user')
    )
    spent = sum((expense.amount for expense in expenses), Decimal('0.00'))
    allocated = sum(
        (
            share.amount_owed
            for expense in expenses
            for share in expense.shares.all()
            if share.user_id == trip.organizer_id
        ),
        Decimal('0.00'),
    )
    return {
        'money': {
            'spent': money(spent, trip.currency),
            'budget': money(trip.total_budget, trip.currency),
            'remaining': f'{money(trip.total_budget - spent, trip.currency)} remaining',
            'spent_pct': int((spent / trip.total_budget) * 100)
            if trip.total_budget else 0,
            'your_share': money(allocated, trip.currency),
            'your_share_note': 'Allocated expenses for the current participant',
            'position': {
                'label': 'Recorded share',
                'amount': money(allocated, trip.currency),
                'note': 'Calculated from the selected participants.',
            },
        },
        'expenses': [
            {
                'name': expense.description,
                'by': expense.paid_by.get_full_name() or expense.paid_by.username,
                'initials': ''.join(
                    part[0] for part in (
                        expense.paid_by.first_name,
                        expense.paid_by.last_name,
                    ) if part
                ).upper()[:2],
                'date': expense.occurred_at.strftime('%a, %b ') + str(expense.occurred_at.day),
                'amount': money(expense.amount, trip.currency),
                'split': f'{expense.shares.count()} participants',
                'everyone': expense.shares.count() == trip.participants.count(),
                'icon': 'wallet',
            }
            for expense in expenses
        ],
    }


def balances_context(trip):
    balances = defaultdict(lambda: Decimal('0.00'))
    for expense in trip.expenses.prefetch_related('shares'):
        balances[expense.paid_by_id] += expense.amount
        for share in expense.shares.all():
            balances[share.user_id] -= share.amount_owed

    users = {user.id: user for user in trip.participants.all()}
    return [
        {
            'name': users[user_id].get_full_name() or users[user_id].username,
            'amount': money(abs(amount), trip.currency),
            'direction': 'gets back' if amount > 0 else 'owes',
        }
        for user_id, amount in balances.items()
        if amount
    ]


def constraints_context(trip):
    return [
        {
            'title': constraint.title,
            'description': constraint.description,
            'active': constraint.is_active,
        }
        for constraint in trip.itinerary_constraints.filter(is_active=True)
    ]


def build_context(trip):
    if not trip.final_destination_id:
        return {'days': [], 'items': [], 'status': 'No final destination'}
    itinerary = getattr(trip.final_destination, 'itinerary', None)
    if itinerary is None:
        return {'days': [], 'items': [], 'status': 'Itinerary not built'}
    items = itinerary.items.select_related('activity')
    return {
        'days': sorted({item.start_at.date() for item in items}),
        'items': [
            {
                'title': item.activity.name,
                'start_at': item.start_at,
                'duration_minutes': item.duration_minutes,
                'reason': item.reason,
            }
            for item in items
        ],
        'status': 'Approved' if itinerary.approved_at else 'Draft',
    }


def create_share_token(trip, user):
    token = secrets.token_urlsafe(24)
    ReadOnlyShareLink.objects.create(
        trip=trip,
        created_by=user,
        token_hash=hashlib.sha256(token.encode()).hexdigest(),
    )
    return token


def token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


def create_invitation(trip, user, email=''):
    """A new invite (FR-06). Only the hash is stored; the raw token is returned
    once, to be put in an email or shown as the group link."""
    token = secrets.token_urlsafe(24)
    TripInvitation.objects.create(
        trip=trip, created_by=user, email=email, token_hash=token_hash(token),
    )
    return token
