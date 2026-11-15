import hashlib
from datetime import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from trips.models import (
    AccommodationProposal,
    AccommodationVote,
    ActivityProposal,
    ActivityScore,
    Destination,
    DestinationVote,
    Expense,
    ExpenseShare,
    Itinerary,
    ItineraryConstraint,
    ItineraryItem,
    ProposalStatus,
    ReadOnlyShareLink,
    TransferProposal,
    TransferVote,
    Trip,
    TripInvitation,
    TripParticipant,
)
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create the shared Trip Sync demo dataset without duplicating existing objects.'

    @staticmethod
    def _user(email, first_name, last_name):
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=email,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            },
        )
        if created:
            user.set_unusable_password()
            user.save(update_fields=['password'])
        return user

    @staticmethod
    def _aware(year, month, day, hour, minute):
        return timezone.make_aware(datetime(year, month, day, hour, minute))

    @staticmethod
    def _token_hash(token):
        return hashlib.sha256(token.encode()).hexdigest()

    @transaction.atomic
    def handle(self, *args, **options):
        users = {
            'vlad': self._user('vlad@example.com', 'Vlad', 'Ghidic'),
            'jules': self._user('jules@example.com', 'Jules', 'Ionescu'),
            'theo': self._user('theo@example.com', 'Theo', 'Pop'),
            'nina': self._user('nina@example.com', 'Nina', 'Radu'),
            'maya': self._user('maya@example.com', 'Maya', 'Dumitru'),
            'leo': self._user('leo@example.com', 'Leo', 'Marin'),
        }

        trip, _ = Trip.objects.get_or_create(
            slug='lisbon',
            defaults={
                'name': 'Lisbon, with the usuals',
                'description': 'Six friends. Two nights.',
                'organizer': users['jules'],
                'departure_date': '2027-06-18',
                'return_date': '2027-06-20',
                'budget_per_person': Decimal('450.00'),
                'currency': 'EUR',
            },
        )
        for user in users.values():
            TripParticipant.objects.get_or_create(trip=trip, user=user)

        destination_data = [
            ('Lisbon', 'Portugal', 'Tiled streets, river views and long dinners in Alfama.'),
            ('Porto', 'Portugal', 'Douro-side wandering and little wine bars.'),
            ('Seville', 'Spain', 'Orange-tree courtyards, tapas and warm evenings.'),
        ]
        destinations = {}
        for city, country, description in destination_data:
            destination, _ = Destination.objects.get_or_create(
                trip=trip,
                city=city,
                country=country,
                defaults={
                    'description': description,
                    'created_by': users['jules'],
                    'status': ProposalStatus.APPROVED,
                },
            )
            destinations[city] = destination
        trip.final_destination = destinations['Lisbon']

        for city, yes_users in {
            'Lisbon': ['jules', 'theo', 'maya'],
            'Porto': ['jules', 'leo'],
            'Seville': ['theo'],
        }.items():
            destination = destinations[city]
            for key, user in users.items():
                DestinationVote.objects.get_or_create(
                    destination=destination,
                    user=user,
                    defaults={'value': key in yes_users},
                )

        accommodations = {}
        for name, address, cost in [
            ('Casa do Pátio', 'Graça', '888.00'),
            ('Alfama Loft', 'Alfama', '936.00'),
            ('Bairro House', 'Príncipe Real', '1128.00'),
        ]:
            accommodation, _ = AccommodationProposal.objects.get_or_create(
                trip=trip,
                name=name,
                defaults={
                    'address': address,
                    'estimated_cost': Decimal(cost),
                    'proposed_by': users['jules'],
                    'status': ProposalStatus.APPROVED,
                },
            )
            accommodations[name] = accommodation
        trip.final_accommodation = accommodations['Casa do Pátio']

        for key in ['jules', 'theo', 'maya']:
            AccommodationVote.objects.get_or_create(
                trip=trip,
                user=users[key],
                defaults={'accommodation': accommodations['Casa do Pátio']},
            )
        AccommodationVote.objects.get_or_create(
            trip=trip,
            user=users['leo'],
            defaults={'accommodation': accommodations['Alfama Loft']},
        )

        transfers = {}
        for name, route, cost, duration in [
            ('One shared van', 'Rossio meeting point to Lisbon airport', '60.00', 45),
            ('Two taxis', 'Two cars to Lisbon airport', '48.00', 50),
            ('Metro together', 'Walk and metro to Lisbon airport', '18.00', 70),
        ]:
            transfer, _ = TransferProposal.objects.get_or_create(
                trip=trip,
                name=name,
                defaults={
                    'route': route,
                    'estimated_cost': Decimal(cost),
                    'duration_minutes': duration,
                    'proposed_by': users['theo'],
                    'status': ProposalStatus.APPROVED,
                },
            )
            transfers[name] = transfer
        trip.final_transfer = transfers['One shared van']

        for key in ['jules', 'theo', 'maya']:
            TransferVote.objects.get_or_create(
                trip=trip,
                user=users[key],
                defaults={'transfer': transfers['One shared van']},
            )
        TransferVote.objects.get_or_create(
            trip=trip,
            user=users['leo'],
            defaults={'transfer': transfers['Two taxis']},
        )

        activities = {}
        activity_data = [
            ('A wander through Alfama', '0.00', 120, 10, 0, 'Alfama'),
            ('Make your own azulejo', '180.00', 120, 14, 0, 'Chiado'),
            ('Saturday sunset sail', '210.00', 120, 18, 30, 'Doca de Belém'),
            ('A pastel de nata pit stop', '30.00', 60, 12, 30, 'Chiado'),
        ]
        for name, cost, duration, hour, minute, place in activity_data:
            activity, _ = ActivityProposal.objects.get_or_create(
                destination=destinations['Lisbon'],
                name=name,
                defaults={
                    'description': place,
                    'estimated_cost': Decimal(cost),
                    'duration_minutes': duration,
                    'start_at': self._aware(2027, 6, 19, hour, minute),
                    'proposed_by': users['nina'],
                    'status': ProposalStatus.APPROVED,
                },
            )
            activities[name] = activity

        scores = {
            'A wander through Alfama': [5, 4, 5, 4],
            'Make your own azulejo': [4, 4, 4, 4],
            'Saturday sunset sail': [3, 5, 5, 4],
            'A pastel de nata pit stop': [2, 4, 4, 5],
        }
        for name, values in scores.items():
            for key, score in zip(['vlad', 'jules', 'theo', 'nina'], values):
                ActivityScore.objects.get_or_create(
                    activity=activities[name],
                    user=users[key],
                    defaults={'score': score},
                )

        itinerary, _ = Itinerary.objects.get_or_create(
            destination=destinations['Lisbon'],
            defaults={
                'approved_at': self._aware(2027, 6, 10, 12, 0),
                'approved_by': users['jules'],
            },
        )
        itinerary_items = [
            ('A wander through Alfama', 10, 0, 0, 'Highest group score at no cost.'),
            ('A pastel de nata pit stop', 12, 30, 1, 'Fits the remaining budget and time.'),
            ('Saturday sunset sail', 18, 30, 2, 'Best score of the day.'),
        ]
        for name, hour, minute, position, reason in itinerary_items:
            ItineraryItem.objects.get_or_create(
                itinerary=itinerary,
                activity=activities[name],
                defaults={
                    'start_at': self._aware(2027, 6, 19, hour, minute),
                    'duration_minutes': activities[name].duration_minutes,
                    'position': position,
                    'reason': reason,
                },
            )

        ItineraryConstraint.objects.get_or_create(
            trip=trip,
            title='Keep Saturday evening free',
            defaults={
                'created_by': users['jules'],
                'description': 'Leave the evening open for the agreed sunset sail.',
            },
        )

        expenses = [
            ('Casa do Pátio deposit', users['jules'], '444.00', '2027-05-22'),
            ('Return train tickets', users['theo'], '312.00', '2027-05-25'),
            ('Sunset sail deposit', users['nina'], '105.00', '2027-06-01'),
            ('Dinner deposit', users['theo'], '60.00', '2027-06-02'),
            ('Taxi from the station', users['maya'], '24.00', '2027-06-18'),
        ]
        for description, payer, amount, occurred_at in expenses:
            expense, created = Expense.objects.get_or_create(
                trip=trip,
                description=description,
                defaults={
                    'paid_by': payer,
                    'amount': Decimal(amount),
                    'currency': trip.currency,
                    'occurred_at': self._aware(
                        *[int(part) for part in occurred_at.split('-')],
                        12,
                        0,
                    ),
                },
            )
            if created:
                share_users = users.values() if description != 'Taxi from the station' else (
                    users['maya'], users['leo'], users['nina']
                )
                share = expense.amount / len(tuple(share_users))
                for user in share_users:
                    ExpenseShare.objects.create(
                        expense=expense,
                        user=user,
                        amount_owed=share,
                    )

        TripInvitation.objects.get_or_create(
            trip=trip,
            token_hash=self._token_hash('7f3b-91ac-24de'),
            defaults={'created_by': users['jules'], 'email': 'friend@example.com'},
        )
        ReadOnlyShareLink.objects.get_or_create(
            trip=trip,
            token_hash=self._token_hash('c41d-8f22-7b90'),
            defaults={'created_by': users['jules']},
        )

        trip.save()
        self.stdout.write(self.style.SUCCESS(
            f'Demo data ready: {trip.name} ({trip.slug})'
        ))
