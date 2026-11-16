"""Account forms: creating an account (FR-01) and signing in (FR-02).

People sign in with their email. The email doubles as the username, which is
how the seeded demo users are stored as well.
"""

from decimal import Decimal, InvalidOperation

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone


class RegisterForm(forms.Form):
    name = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(strip=False, widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        User = get_user_model()
        if User.objects.filter(email__iexact=email).exists() or \
                User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError(
                'An account with this email already exists. Sign in instead.'
            )
        return email

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('password')
        if password:
            first, _, last = cleaned.get('name', '').strip().partition(' ')
            candidate = get_user_model()(
                username=cleaned.get('email', ''),
                email=cleaned.get('email', ''),
                first_name=first,
                last_name=last,
            )
            try:
                validate_password(password, candidate)
            except forms.ValidationError as error:
                self.add_error('password', error)
        return cleaned

    def save(self):
        first, _, last = self.cleaned_data['name'].strip().partition(' ')
        email = self.cleaned_data['email']
        return get_user_model().objects.create_user(
            username=email,
            email=email,
            password=self.cleaned_data['password'],
            first_name=first,
            last_name=last.strip(),
        )


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(strip=False, widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': 'That email and password don’t match an account.',
        'inactive': 'This account has been disabled.',
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get('email')
        password = cleaned.get('password')
        if email and password:
            User = get_user_model()
            account = User.objects.filter(email__iexact=email).first()
            username = account.get_username() if account else email
            self.user = authenticate(
                self.request, username=username, password=password,
            )
            if self.user is None:
                if account is not None and not account.is_active:
                    raise forms.ValidationError(self.error_messages['inactive'])
                raise forms.ValidationError(self.error_messages['invalid_login'])
        return cleaned


# ---- Creating a trip (FR-03, FR-04, FR-05) ----------------------------------
#
# The flow has one form per step. Each step is validated on its own and kept in
# the session; the trip is only written to the database after the last step,
# because dates and budget are required columns on Trip.

TRIP_CURRENCIES = ['RON', 'EUR', 'USD']
MAX_TRIP_DAYS = 60
MAX_BUDGET = Decimal('9999999999.99')  # what Trip.budget_per_person can hold


class TripBasicsForm(forms.Form):
    """Step 1 (FR-03): the name is required, the description is optional."""

    name = forms.CharField(
        max_length=200,
        error_messages={
            'required': 'Give the trip a name.',
            'max_length': 'Keep the name under 200 characters.',
        },
    )
    description = forms.CharField(required=False, widget=forms.Textarea)
    # Where the group is going, if the organizer already knows. Left empty,
    # the group proposes destinations and votes on them later (FR-10, FR-14).
    city = forms.CharField(required=False, max_length=100)
    country = forms.CharField(required=False, max_length=100)

    def clean(self):
        cleaned = super().clean()
        city, country = cleaned.get('city'), cleaned.get('country')
        if city and not country:
            self.add_error('country', 'Add the country as well.')
        if country and not city:
            self.add_error('city', 'Add the city as well.')
        return cleaned


class TripDatesForm(forms.Form):
    """Step 2 (FR-04): the dates, from which the length of the trip follows."""

    start = forms.DateField(error_messages={
        'required': 'Pick the day you leave.',
        'invalid': 'Enter a valid date.',
    })
    end = forms.DateField(error_messages={
        'required': 'Pick the day you come back.',
        'invalid': 'Enter a valid date.',
    })

    def clean_start(self):
        start = self.cleaned_data['start']
        if start < timezone.localdate():
            raise forms.ValidationError('The trip can’t start in the past.')
        return start

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get('start'), cleaned.get('end')
        if start and end:
            if end < start:
                self.add_error('end', 'You can’t come back before you leave.')
            elif (end - start).days + 1 > MAX_TRIP_DAYS:
                self.add_error('end', f'A trip can last at most {MAX_TRIP_DAYS} days.')
        return cleaned


class TripBudgetForm(forms.Form):
    """Step 3 (FR-05): the total budget, its currency and how many people share it."""

    budget = forms.CharField(error_messages={'required': 'Set a budget for the trip.'})
    currency = forms.ChoiceField(
        choices=[(code, code) for code in TRIP_CURRENCIES],
        error_messages={'invalid_choice': 'Pick one of the listed currencies.'},
    )
    group_size = forms.IntegerField(
        min_value=1,
        max_value=50,
        error_messages={
            'required': 'How many people are going?',
            'invalid': 'Enter a whole number.',
            'min_value': 'At least one person goes: you.',
            'max_value': 'Groups are capped at 50 people.',
        },
    )

    def clean_budget(self):
        """Accept '1500', '1 500', '1500.50' and the Romanian '1500,50'."""
        raw = self.cleaned_data['budget'].replace(' ', '').replace(' ', '')
        if ',' in raw and '.' not in raw:
            raw = raw.replace(',', '.')
        else:
            raw = raw.replace(',', '')
        try:
            amount = Decimal(raw)
        except InvalidOperation:
            raise forms.ValidationError('Enter the budget as a number, e.g. 1500.')
        if not amount.is_finite() or amount <= 0:
            raise forms.ValidationError('The budget has to be more than zero.')
        if amount.as_tuple().exponent < -2:
            raise forms.ValidationError('Use at most two decimals.')
        if amount > MAX_BUDGET:
            raise forms.ValidationError('That budget is too large.')
        return amount


class TripInviteForm(forms.Form):
    """Step 4 (FR-06): invite one person by email."""

    invite = forms.EmailField(error_messages={
        'required': 'Enter an email address.',
        'invalid': 'Enter a valid email address.',
    })

    def __init__(self, *args, trip, inviter, **kwargs):
        self.trip = trip
        self.inviter = inviter
        super().__init__(*args, **kwargs)

    def clean_invite(self):
        email = self.cleaned_data['invite'].strip().lower()
        if email == (self.inviter.email or '').lower():
            raise forms.ValidationError('That’s you, and you’re already in.')
        if self.trip.participants.filter(email__iexact=email).exists():
            raise forms.ValidationError('They’re already in the group.')
        if self.trip.invitations.filter(
            email__iexact=email, revoked_at__isnull=True, accepted_at__isnull=True,
        ).exists():
            raise forms.ValidationError('You’ve already invited them.')
        return email
