from trips.models import ActivityProposal, Trip

from .db_context import trip_context, user_context


class UiData:
    """Compatibility context for prototype screens, backed by the database."""

    def __getattr__(self, name):
        trip = Trip.objects.order_by('id').first()
        if trip is None:
            return self._empty(name)
        if name == 'TRIP':
            return trip_context(trip)
        if name == 'USER':
            return user_context(trip.organizer)
        if name == 'FRIENDS':
            return trip_context(trip)['friends']
        if name == 'NEXT_DECISION':
            return self._next_decision(trip)
        if name == 'DECISIONS':
            return self._decisions(trip)
        if name == 'DECISION_ORDER':
            return list(self._decisions(trip))
        if name == 'DECISION_CHAIN':
            return self._decision_chain(trip)
        if name == 'PROPOSALS':
            return {'pending': [], 'approved': [], 'rejected': []}
        if name == 'ITINERARY':
            return {}
        if name == 'ITINERARY_MAP':
            return {}
        if name == 'MONEY':
            return {}
        if name == 'EXPENSES':
            return []
        if name == 'BALANCES':
            return []
        if name == 'SHARED_ITINERARY':
            return {'trip': trip_context(trip), 'days': []}
        if name == 'SHARE':
            token = 'c41d-8f22-7b90'
            return {
                'title': 'Share the itinerary',
                'lede': 'A read-only view for anyone with the link.',
                'token': token,
                'link': f'/share/{token}/',
                'created': 'Created from the current itinerary',
                'views': 'Read-only access',
                'shown': ['Final destination', 'Approved itinerary'],
                'hidden': ['Votes', 'Expenses'],
                'revoke_note': 'Revoking the link immediately removes access.',
                'expired': {'title': 'This link is no longer available.'},
            }
        if name == 'JOIN':
            return self._join(trip)
        if name == 'DRAFT_TRIP':
            return {'name': '', 'destination': '', 'dates': '', 'budget': ''}
        if name == 'DRAFT_SUMMARY':
            return []
        if name == 'NEW_TRIP_STEPS':
            return [
                {'slug': 'basics', 'title': 'Trip basics'},
                {'slug': 'dates', 'title': 'Dates'},
                {'slug': 'budget', 'title': 'Budget'},
                {'slug': 'review', 'title': 'Review'},
            ]
        if name == 'NEW_EXPENSE':
            return {'name': '', 'amount': '', 'date': ''}
        if name == 'PROPOSE_FORMS':
            return {
                kind: {'title': f'Propose {kind}', 'fields': []}
                for kind in ('activity', 'destination', 'accommodation', 'transfer')
            }
        if name == 'CLOSE_VOTE':
            return {'voted': 0, 'voters': trip.participants.count()}
        if name == 'CONSTRAINTS':
            return {'items': []}
        if name == 'BUILD':
            return {'days': []}
        return self._empty(name)

    def _next_decision(self, trip):
        proposal = ActivityProposal.objects.filter(
            destination=trip.final_destination,
        ).first() if trip.final_destination_id else None
        return {
            'slug': 'activities',
            'title': 'Activities',
            'summary': proposal.name if proposal else 'No activity proposals yet.',
            'due': 'Open',
            'voted': 0,
            'voters': trip.participants.count(),
        }

    def _decisions(self, trip):
        activities = ActivityProposal.objects.filter(
            destination=trip.final_destination,
        ) if trip.final_destination_id else ActivityProposal.objects.none()
        options = [
            {
                'name': activity.name,
                'cost': str(activity.estimated_cost),
                'duration': f'{activity.duration_minutes} min',
                'score': '—',
                'submitted': 0,
                'my_score': 0,
                'photo': 'default',
            }
            for activity in activities
        ]
        return {
            'activities': {
                'index': 'Decision 1',
                'title': 'Choose activities',
                'lede': 'Review the activities proposed for this trip.',
                'note': 'Scores are collected from trip participants.',
                'stats': [],
                'options': options,
                'voted': 0,
                'voters': trip.participants.count(),
            },
        }

    def _decision_chain(self, trip):
        return [
            {
                'slug': 'activities',
                'number': 1,
                'kind': 'Activities',
                'title': 'Choose activities',
                'blurb': 'Select the activities for the itinerary.',
                'result': '',
                'meta': f'{ActivityProposal.objects.filter(destination=trip.final_destination).count()} proposals',
                'state': 'open',
                'status': 'Open',
                'cta': 'Vote',
                'route': 'decision',
            },
        ]

    def _join(self, trip):
        return {
            'signup': {'title': f'Join {trip.name}', 'lede': 'Create an account to join this trip.'},
            'signin': {'title': f'Sign in to {trip.name}', 'lede': 'Sign in to continue.'},
            'welcome': {'title': 'You are in.', 'lede': 'The trip is ready to plan together.'},
            'expired': {'title': 'This invitation is no longer available.'},
        }

    @staticmethod
    def _empty(name):
        return {} if name.isupper() else []


ui = UiData()
