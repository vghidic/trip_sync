from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


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
