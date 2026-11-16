"""Account forms: creating an account (FR-01) and signing in (FR-02).

People sign in with their email. The email doubles as the username, which is
how the seeded demo users are stored as well.
"""

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password


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
