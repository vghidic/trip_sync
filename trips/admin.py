from django.contrib import admin

from .models import (
    ActivityProposal,
    ActivityScore,
    AccommodationProposal,
    AccommodationVote,
    Destination,
    DestinationVote,
    Expense,
    ExpenseShare,
    Itinerary,
    ItineraryItem,
    ReadOnlyShareLink,
    TransferProposal,
    TransferVote,
    Trip,
    TripInvitation,
    TripParticipant,
)


admin.site.register([
    Trip,
    TripParticipant,
    TripInvitation,
    Destination,
    DestinationVote,
    ActivityProposal,
    ActivityScore,
    AccommodationProposal,
    AccommodationVote,
    TransferProposal,
    TransferVote,
    Itinerary,
    ItineraryItem,
    Expense,
    ExpenseShare,
    ReadOnlyShareLink,
])
