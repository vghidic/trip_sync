from decimal import Decimal
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Q
from django.utils.text import slugify


class ProposalStatus(models.TextChoices):
    PROPOSED = 'proposed', 'Proposed'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    REMOVED = 'removed', 'Removed'


class Trip(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='organized_trips',
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='TripParticipant',
        related_name='trips',
    )
    departure_date = models.DateField()
    return_date = models.DateField()
    budget_per_person = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    currency = models.CharField(max_length=3, default='RON')
    final_destination = models.ForeignKey(
        'Destination',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='final_for_trips',
    )
    final_accommodation = models.ForeignKey(
        'AccommodationProposal',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='final_for_trips',
    )
    final_transfer = models.ForeignKey(
        'TransferProposal',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='final_for_trips',
    )
    voting_closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or 'trip'
            self.slug = base_slug
            suffix = 2
            while Trip.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f'{base_slug}-{suffix}'
                suffix += 1
        super().save(*args, **kwargs)
        TripParticipant.objects.get_or_create(trip=self, user=self.organizer)

    def clean(self):
        errors = {}
        if self.return_date < self.departure_date:
            errors['return_date'] = 'Return date cannot be before departure date.'
        if self.final_destination_id:
            if self.final_destination.trip_id != self.pk:
                errors['final_destination'] = 'Final destination must belong to this trip.'
        if self.final_accommodation_id:
            if self.final_accommodation.trip_id != self.pk:
                errors['final_accommodation'] = 'Final accommodation must belong to this trip.'
        if self.final_transfer_id:
            if self.final_transfer.trip_id != self.pk:
                errors['final_transfer'] = 'Final transfer must belong to this trip.'
        if errors:
            raise ValidationError(errors)

    @property
    def total_budget(self):
        return self.budget_per_person * self.participants.count()

    def __str__(self):
        return self.name


class TripParticipant(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['trip', 'user'],
                name='unique_trip_participant',
            ),
        ]

    def __str__(self):
        return f'{self.user} - {self.trip}'


class TripInvitation(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='invitations')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_trip_invitations',
    )
    email = models.EmailField(blank=True)
    token_hash = models.CharField(max_length=128, unique=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='accepted_trip_invitations',
    )
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.created_by_id and self.trip_id and not TripParticipant.objects.filter(
            trip_id=self.trip_id, user_id=self.created_by_id
        ).exists():
            raise ValidationError({'created_by': 'Only trip participants can create invitations.'})

    @property
    def is_active(self):
        from django.utils import timezone

        return (
            self.revoked_at is None
            and self.accepted_at is None
            and (self.expires_at is None or self.expires_at > timezone.now())
        )


class Destination(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='destinations')
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=20,
        choices=ProposalStatus.choices,
        default=ProposalStatus.PROPOSED,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='destination_proposals',
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('-90')), MaxValueValidator(Decimal('90'))],
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('-180')), MaxValueValidator(Decimal('180'))],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['city', 'country']

    def clean(self):
        if self.created_by_id and self.trip_id and not TripParticipant.objects.filter(
            trip_id=self.trip_id, user_id=self.created_by_id
        ).exists():
            raise ValidationError({'created_by': 'The proposer must participate in this trip.'})

    def __str__(self):
        return f'{self.city}, {self.country}'


class DestinationVote(models.Model):
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name='votes',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='destination_votes',
    )
    value = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['destination', 'user'],
                name='unique_destination_vote',
            ),
        ]

    def clean(self):
        if self.destination_id and self.user_id:
            if not TripParticipant.objects.filter(
                trip_id=self.destination.trip_id, user_id=self.user_id
            ).exists():
                raise ValidationError({'user': 'Only trip participants can vote.'})


class ActivityProposal(models.Model):
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name='activity_proposals',
    )
    proposed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='activity_proposals',
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=ProposalStatus.choices,
        default=ProposalStatus.PROPOSED,
    )
    estimated_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    duration_minutes = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    start_at = models.DateTimeField()
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('-90')), MaxValueValidator(Decimal('90'))],
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('-180')), MaxValueValidator(Decimal('180'))],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_at', 'name']

    @property
    def end_at(self):
        return self.start_at + timedelta(minutes=self.duration_minutes)

    def clean(self):
        if self.proposed_by_id and self.destination_id:
            if not TripParticipant.objects.filter(
                trip_id=self.destination.trip_id, user_id=self.proposed_by_id
            ).exists():
                raise ValidationError({'proposed_by': 'Only trip participants can propose activities.'})

    def __str__(self):
        return self.name


class AccommodationProposal(models.Model):
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='accommodation_proposals',
    )
    proposed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='accommodation_proposals',
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    estimated_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    status = models.CharField(
        max_length=20,
        choices=ProposalStatus.choices,
        default=ProposalStatus.PROPOSED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.proposed_by_id and self.trip_id and not TripParticipant.objects.filter(
            trip_id=self.trip_id, user_id=self.proposed_by_id
        ).exists():
            raise ValidationError({'proposed_by': 'Only trip participants can propose accommodation.'})

    def __str__(self):
        return self.name


class AccommodationVote(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='accommodation_votes')
    accommodation = models.ForeignKey(
        AccommodationProposal,
        on_delete=models.CASCADE,
        related_name='votes',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='accommodation_votes',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['trip', 'user'],
                name='unique_accommodation_vote_per_trip_user',
            ),
        ]

    def clean(self):
        if self.accommodation_id and self.trip_id and self.accommodation.trip_id != self.trip_id:
            raise ValidationError({'accommodation': 'Accommodation must belong to this trip.'})
        if self.user_id and self.trip_id and not TripParticipant.objects.filter(
            trip_id=self.trip_id, user_id=self.user_id
        ).exists():
            raise ValidationError({'user': 'Only trip participants can vote.'})


class TransferProposal(models.Model):
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='transfer_proposals',
    )
    proposed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='transfer_proposals',
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    route = models.CharField(max_length=255, blank=True)
    estimated_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    duration_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
    )
    status = models.CharField(
        max_length=20,
        choices=ProposalStatus.choices,
        default=ProposalStatus.PROPOSED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.proposed_by_id and self.trip_id and not TripParticipant.objects.filter(
            trip_id=self.trip_id, user_id=self.proposed_by_id
        ).exists():
            raise ValidationError({'proposed_by': 'Only trip participants can propose transfers.'})

    def __str__(self):
        return self.name


class TransferVote(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='transfer_votes')
    transfer = models.ForeignKey(
        TransferProposal,
        on_delete=models.CASCADE,
        related_name='votes',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='transfer_votes',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['trip', 'user'],
                name='unique_transfer_vote_per_trip_user',
            ),
        ]

    def clean(self):
        if self.transfer_id and self.trip_id and self.transfer.trip_id != self.trip_id:
            raise ValidationError({'transfer': 'Transfer must belong to this trip.'})
        if self.user_id and self.trip_id and not TripParticipant.objects.filter(
            trip_id=self.trip_id, user_id=self.user_id
        ).exists():
            raise ValidationError({'user': 'Only trip participants can vote.'})


class ActivityScore(models.Model):
    activity = models.ForeignKey(
        ActivityProposal,
        on_delete=models.CASCADE,
        related_name='scores',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='activity_scores',
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['activity', 'user'],
                name='unique_activity_score',
            ),
            models.CheckConstraint(
                condition=Q(score__gte=1) & Q(score__lte=5),
                name='activity_score_between_one_and_five',
            ),
        ]

    def clean(self):
        if self.activity_id and self.user_id:
            if not TripParticipant.objects.filter(
                trip_id=self.activity.destination.trip_id, user_id=self.user_id
            ).exists():
                raise ValidationError({'user': 'Only trip participants can score activities.'})


class Itinerary(models.Model):
    destination = models.OneToOneField(
        Destination,
        on_delete=models.CASCADE,
        related_name='itinerary',
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='approved_itineraries',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.destination_id and self.destination.trip.final_destination_id != self.destination_id:
            raise ValidationError(
                {'destination': 'An itinerary can only be created for the final destination.'}
            )
        if self.approved_by_id and not TripParticipant.objects.filter(
            trip_id=self.destination.trip_id, user_id=self.approved_by_id
        ).exists():
            raise ValidationError({'approved_by': 'Only trip participants can approve itineraries.'})


class ItineraryConstraint(models.Model):
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='itinerary_constraints',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_itinerary_constraints',
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.created_by_id and self.trip_id and not TripParticipant.objects.filter(
            trip_id=self.trip_id, user_id=self.created_by_id
        ).exists():
            raise ValidationError(
                {'created_by': 'Only trip participants can add itinerary constraints.'}
            )


class ItineraryItem(models.Model):
    itinerary = models.ForeignKey(
        Itinerary,
        on_delete=models.CASCADE,
        related_name='items',
    )
    activity = models.ForeignKey(
        ActivityProposal,
        on_delete=models.PROTECT,
        related_name='itinerary_items',
    )
    start_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    position = models.PositiveIntegerField(default=0)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_at', 'position']
        constraints = [
            models.UniqueConstraint(
                fields=['itinerary', 'activity'],
                name='unique_itinerary_activity',
            ),
        ]

    @property
    def end_at(self):
        return self.start_at + timedelta(minutes=self.duration_minutes)

    def clean(self):
        if self.itinerary_id and self.activity_id:
            if self.activity.destination_id != self.itinerary.destination_id:
                raise ValidationError({'activity': 'Activity must belong to the itinerary destination.'})


class Expense(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='expenses')
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='paid_expenses',
    )
    description = models.CharField(max_length=255)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    currency = models.CharField(max_length=3)
    occurred_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.paid_by_id and self.trip_id and not TripParticipant.objects.filter(
            trip_id=self.trip_id, user_id=self.paid_by_id
        ).exists():
            raise ValidationError({'paid_by': 'Only trip participants can pay expenses.'})

    def __str__(self):
        return self.description


class ExpenseShare(models.Model):
    expense = models.ForeignKey(
        Expense,
        on_delete=models.CASCADE,
        related_name='shares',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='expense_shares',
    )
    amount_owed = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['expense', 'user'],
                name='unique_expense_share',
            ),
        ]

    def clean(self):
        if self.user_id and self.expense_id and not TripParticipant.objects.filter(
            trip_id=self.expense.trip_id, user_id=self.user_id
        ).exists():
            raise ValidationError({'user': 'Only trip participants can have expense shares.'})


class ReadOnlyShareLink(models.Model):
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='read_only_links',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_read_only_links',
    )
    token_hash = models.CharField(max_length=128, unique=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.created_by_id and self.trip_id and not TripParticipant.objects.filter(
            trip_id=self.trip_id, user_id=self.created_by_id
        ).exists():
            raise ValidationError({'created_by': 'Only trip participants can create share links.'})

    @property
    def is_active(self):
        from django.utils import timezone

        return (
            self.revoked_at is None
            and (self.expires_at is None or self.expires_at > timezone.now())
        )
