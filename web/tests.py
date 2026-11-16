from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from trips.models import Destination, Trip, TripInvitation, TripParticipant


class AuthTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='ana@example.com',
            email='ana@example.com',
            password='a-long-secret-1',
            first_name='Ana',
        )

    def test_pages_need_login(self):
        response = self.client.get(reverse('web:trips'))
        self.assertRedirects(
            response, reverse('web:login') + '?next=/', fetch_redirect_response=False,
        )

    def test_login_and_register_pages_are_public(self):
        self.assertEqual(self.client.get(reverse('web:login')).status_code, 200)
        self.assertEqual(self.client.get(reverse('web:register')).status_code, 200)

    def test_register_creates_user_and_signs_in(self):
        response = self.client.post(reverse('web:register'), {
            'name': 'Mara Pop',
            'email': 'Mara@Example.com',
            'password': 'a-long-secret-2',
        })
        self.assertRedirects(response, reverse('web:trips'), fetch_redirect_response=False)
        user = get_user_model().objects.get(email='mara@example.com')
        self.assertEqual((user.first_name, user.last_name), ('Mara', 'Pop'))
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_register_rejects_duplicate_email_and_weak_password(self):
        response = self.client.post(reverse('web:register'), {
            'name': 'Ana', 'email': 'ANA@example.com', 'password': '123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('email', response.context['form'].errors)
        self.assertIn('password', response.context['form'].errors)

    def test_login_with_email(self):
        response = self.client.post(reverse('web:login'), {
            'email': 'ANA@example.com', 'password': 'a-long-secret-1',
        })
        self.assertRedirects(response, reverse('web:trips'), fetch_redirect_response=False)

    def test_login_follows_safe_next_only(self):
        data = {'email': 'ana@example.com', 'password': 'a-long-secret-1'}
        response = self.client.post(reverse('web:login') + '?next=/styleguide/', data)
        self.assertRedirects(response, '/styleguide/', fetch_redirect_response=False)
        self.client.logout()
        response = self.client.post(
            reverse('web:login') + '?next=https://evil.example/', data,
        )
        self.assertRedirects(response, reverse('web:trips'), fetch_redirect_response=False)

    def test_wrong_password_shows_error(self):
        response = self.client.post(reverse('web:login'), {
            'email': 'ana@example.com', 'password': 'nope',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'don’t match an account')

    def test_logout_requires_post(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('web:logout')).status_code, 405)
        response = self.client.post(reverse('web:logout'))
        self.assertRedirects(response, reverse('web:login'), fetch_redirect_response=False)
        self.assertNotIn('_auth_user_id', self.client.session)


class NewTripTests(TestCase):
    """Creating a trip (SCRUM-7) and setting its dates and budget (SCRUM-8, SCRUM-9)."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='ana@example.com', email='ana@example.com',
            password='a-long-secret-1', first_name='Ana',
        )
        self.client.force_login(self.user)
        today = timezone.localdate()
        self.start = today + timedelta(days=10)
        self.end = today + timedelta(days=13)

    def step_url(self, step):
        return reverse('web:new_trip_step', args=[step])

    def post_basics(self, name='Weekend la munte', description='', city='', country=''):
        return self.client.post(self.step_url('basics'), {
            'name': name, 'description': description, 'city': city, 'country': country,
        })

    def post_dates(self, start=None, end=None):
        return self.client.post(self.step_url('when'), {
            'start': (start or self.start).isoformat(),
            'end': (end or self.end).isoformat(),
        })

    def post_budget(self, budget='2000', currency='RON', group_size='4'):
        return self.client.post(self.step_url('budget'), {
            'budget': budget, 'currency': currency, 'group_size': group_size,
        })

    def create_trip(self, **basics):
        self.post_basics(**basics)
        self.post_dates()
        self.post_budget()
        return Trip.objects.latest('created_at')

    def test_first_step_renders_without_any_trip_in_the_database(self):
        self.assertFalse(Trip.objects.exists())
        self.assertEqual(self.client.get(reverse('web:new_trip')).status_code, 200)

    def test_every_step_renders(self):
        self.post_basics()
        self.post_dates()
        for step in ('basics', 'when', 'budget'):
            self.assertEqual(self.client.get(self.step_url(step)).status_code, 200)

    def test_name_is_required(self):
        response = self.post_basics(name='   ')
        self.assertEqual(response.status_code, 200)
        self.assertIn('name', response.context['form'].errors)
        self.assertFalse(Trip.objects.exists())

    def test_full_flow_creates_trip_with_creator_as_organizer(self):
        self.assertRedirects(self.post_basics(description='Doar noi patru'),
                             self.step_url('when'), fetch_redirect_response=False)
        self.assertRedirects(self.post_dates(), self.step_url('budget'),
                             fetch_redirect_response=False)
        response = self.post_budget()

        trip = Trip.objects.get()
        # The trip exists as soon as the budget is in; then come the invites.
        self.assertRedirects(response, self.step_url('invite'))
        self.assertEqual(trip.name, 'Weekend la munte')
        self.assertEqual(trip.description, 'Doar noi patru')
        self.assertEqual(trip.organizer, self.user)
        self.assertTrue(TripParticipant.objects.filter(trip=trip, user=self.user).exists())
        self.assertEqual((trip.departure_date, trip.return_date), (self.start, self.end))
        self.assertEqual(trip.currency, 'RON')
        self.assertEqual(trip.budget_per_person, Decimal('500.00'))
        self.assertNotIn('new_trip_draft', self.client.session)
        self.assertIsNone(trip.final_destination)

        response = self.client.post(self.step_url('invite'), {'action': 'done'})
        self.assertRedirects(response, reverse('web:trip_overview', args=[trip.slug]))

    def test_description_is_optional(self):
        self.post_basics(description='')
        self.post_dates()
        self.post_budget()
        self.assertEqual(Trip.objects.get().description, '')

    def test_new_trip_shows_in_my_list_only(self):
        self.post_basics(name='Grupul meu')
        self.post_dates()
        self.post_budget()
        self.assertContains(self.client.get(reverse('web:trips')), 'Grupul meu')

        other = get_user_model().objects.create_user(
            username='dan@example.com', email='dan@example.com', password='a-long-secret-3',
        )
        self.client.force_login(other)
        response = self.client.get(reverse('web:trips'))
        self.assertNotContains(response, 'Grupul meu')
        self.assertContains(response, 'No trips yet')

    def test_return_before_departure_is_rejected(self):
        self.post_basics()
        response = self.post_dates(start=self.end, end=self.start)
        self.assertEqual(response.status_code, 200)
        self.assertIn('end', response.context['form'].errors)

    def test_start_in_the_past_is_rejected(self):
        self.post_basics()
        yesterday = timezone.localdate() - timedelta(days=1)
        response = self.post_dates(start=yesterday, end=self.end)
        self.assertIn('start', response.context['form'].errors)

    def test_one_day_trip_is_allowed(self):
        self.post_basics()
        response = self.post_dates(start=self.start, end=self.start)
        self.assertRedirects(response, self.step_url('budget'), fetch_redirect_response=False)

    def test_budget_must_be_a_positive_number(self):
        self.post_basics()
        self.post_dates()
        for bad in ('0', '-5', 'abc', '12.345'):
            response = self.post_budget(budget=bad)
            self.assertIn('budget', response.context['form'].errors, bad)
        response = self.post_budget(group_size='0')
        self.assertIn('group_size', response.context['form'].errors)
        response = self.post_budget(currency='XYZ')
        self.assertIn('currency', response.context['form'].errors)
        self.assertFalse(Trip.objects.exists())

    def test_budget_accepts_romanian_decimal_comma(self):
        self.post_basics()
        self.post_dates()
        self.post_budget(budget='1 500,50', currency='EUR', group_size='3')
        trip = Trip.objects.get()
        self.assertEqual(trip.budget_per_person, Decimal('500.17'))
        self.assertEqual(trip.currency, 'EUR')

    def test_cannot_skip_ahead(self):
        response = self.client.get(self.step_url('budget'))
        self.assertRedirects(response, self.step_url('basics'), fetch_redirect_response=False)
        self.post_basics()
        response = self.post_budget()
        self.assertRedirects(response, self.step_url('when'), fetch_redirect_response=False)
        self.assertFalse(Trip.objects.exists())

    def test_answers_are_kept_when_going_back(self):
        self.post_basics(name='Revin la nume')
        response = self.client.get(self.step_url('basics'))
        self.assertContains(response, 'value="Revin la nume"')

    def test_same_name_gets_a_unique_slug(self):
        for _ in range(2):
            self.post_basics(name='Lisabona')
            self.post_dates()
            self.post_budget()
        self.assertEqual(
            sorted(Trip.objects.values_list('slug', flat=True)),
            ['lisabona', 'lisabona-2'],
        )

    def test_unknown_step_is_404(self):
        self.assertEqual(self.client.get(self.step_url('nope')).status_code, 404)

    def test_destination_is_optional_and_saved_when_given(self):
        trip = self.create_trip(name='Lisabona', city='Lisbon', country='Portugal')
        destination = trip.final_destination
        self.assertEqual((destination.city, destination.country), ('Lisbon', 'Portugal'))
        self.assertEqual(destination.trip, trip)
        self.assertEqual(destination.status, 'approved')
        self.assertEqual(Destination.objects.count(), 1)

    def test_city_without_country_is_rejected(self):
        response = self.post_basics(city='Lisbon')
        self.assertIn('country', response.context['form'].errors)

    def test_budget_step_sends_you_to_invites(self):
        self.post_basics()
        self.post_dates()
        response = self.post_budget()
        self.assertRedirects(response, self.step_url('invite'), fetch_redirect_response=False)


class InviteStepTests(TestCase):
    """Inviting people while creating the trip (FR-06)."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='ana@example.com', email='ana@example.com',
            password='a-long-secret-1', first_name='Ana',
        )
        self.client.force_login(self.user)
        start = timezone.localdate() + timedelta(days=10)
        url = lambda step: reverse('web:new_trip_step', args=[step])
        self.client.post(url('basics'), {'name': 'Munte'})
        self.client.post(url('when'), {
            'start': start.isoformat(),
            'end': (start + timedelta(days=2)).isoformat(),
        })
        self.client.post(url('budget'), {
            'budget': '900', 'currency': 'RON', 'group_size': '3',
        })
        self.trip = Trip.objects.get()
        self.url = url('invite')

    def invite(self, email):
        return self.client.post(self.url, {'action': 'add', 'invite': email})

    def test_group_link_is_shown_once_and_stored_as_hash(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        link = response.context['invite_link']
        self.assertIn('/join/', link)
        token = link.rstrip('/').rsplit('/', 1)[1]
        invitation = self.trip.invitations.get(email='')
        self.assertNotEqual(invitation.token_hash, token)
        self.assertNotIn(token, str(dict(self.client.session)))

        # Reloading shows no link and makes no second one.
        response = self.client.get(self.url)
        self.assertEqual(response.context['invite_link'], '')
        self.assertEqual(self.trip.invitations.filter(email='').count(), 1)

    def test_invite_by_email_creates_invitation_and_sends_mail(self):
        response = self.invite('Dan@Example.com')
        self.assertRedirects(response, self.url, fetch_redirect_response=False)
        invitation = self.trip.invitations.get(email='dan@example.com')
        self.assertEqual(invitation.created_by, self.user)
        self.assertTrue(invitation.is_active)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['dan@example.com'])
        self.assertIn('/join/', mail.outbox[0].body)
        self.assertContains(self.client.get(self.url), 'dan@example.com')

    def test_invalid_duplicate_and_own_email_are_rejected(self):
        self.invite('dan@example.com')
        for email in ('not-an-email', 'DAN@example.com', 'ana@example.com'):
            response = self.invite(email)
            self.assertEqual(response.status_code, 200, email)
            self.assertIn('invite', response.context['form'].errors, email)
        self.assertEqual(self.trip.invitations.exclude(email='').count(), 1)

    def test_removing_an_invite_revokes_it(self):
        self.invite('dan@example.com')
        invitation = self.trip.invitations.get(email='dan@example.com')
        self.client.post(self.url, {'action': f'remove:{invitation.pk}'})
        invitation.refresh_from_db()
        self.assertFalse(invitation.is_active)
        self.assertNotContains(self.client.get(self.url), 'dan@example.com')

    def test_new_link_revokes_the_old_one(self):
        self.client.get(self.url)
        old = self.trip.invitations.get(email='')
        response = self.client.post(self.url, {'action': 'new_link'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('/join/', response.context['invite_link'])
        self.assertFalse(response.context['form'].errors)
        old.refresh_from_db()
        self.assertFalse(old.is_active)
        self.assertEqual(
            self.trip.invitations.filter(email='', revoked_at__isnull=True).count(), 1,
        )

    def test_invited_person_joins_the_right_trip(self):
        self.invite('dan@example.com')
        link = mail.outbox[0].body.split('Join the group here: ')[1].split()[0]
        self.client.logout()

        response = self.client.get(link)
        self.assertContains(response, 'Join Munte')
        response = self.client.post(link, {
            'name': 'Dan Pop', 'email': 'dan@example.com', 'password': 'a-long-secret-2',
        })
        dan = get_user_model().objects.get(email='dan@example.com')
        self.assertTrue(TripParticipant.objects.filter(trip=self.trip, user=dan).exists())

        # Back on the invite page, Dan shows as joined, not as still invited.
        self.client.force_login(self.user)
        session = self.client.session
        session['new_trip_created'] = {'slug': self.trip.slug, 'draft': {}}
        session.save()
        response = self.client.get(self.url)
        self.assertEqual(response.context['members'], [dan])
        self.assertEqual(response.context['invited'], [])

    def test_revoked_link_goes_to_expired_page(self):
        self.invite('dan@example.com')
        link = mail.outbox[0].body.split('Join the group here: ')[1].split()[0]
        self.client.post(self.url, {
            'action': f'remove:{self.trip.invitations.get(email="dan@example.com").pk}',
        })
        self.client.logout()
        self.assertRedirects(self.client.get(link), reverse('web:join_expired'),
                             fetch_redirect_response=False)

    def test_only_the_creator_reaches_the_invite_step(self):
        other = get_user_model().objects.create_user(
            username='dan@example.com', email='dan@example.com', password='a-long-secret-3',
        )
        self.client.force_login(other)
        self.assertRedirects(self.client.get(self.url), reverse('web:new_trip'),
                             fetch_redirect_response=False)

    def test_overview_shows_budget_per_person(self):
        response = self.client.get(reverse('web:trip_overview', args=[self.trip.slug]))
        self.assertContains(response, '300 RON / person')
