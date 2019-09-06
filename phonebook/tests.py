from django.test import TestCase
from django.contrib.auth.models import User
from mixer.backend.django import mixer
from django.urls import reverse_lazy
from phonebook.forms import PhoneBookForm
from phonebook.models import PhoneBook
from rest_framework.authtoken.models import Token


class PhoneBookTestCase(TestCase):
    def setUp(self):
        self.session_user = mixer.blend(User)
        self.client.force_login(self.session_user)
        self.token = Token.objects.create(user=self.session_user).key
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Token ' + self.token

    def test_phone_book_creation(self):
        phone_books_count = PhoneBook.objects.count()
        response = self.client.post(reverse_lazy("phonebook:create"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(phone_books_count+1, PhoneBook.objects.count())

    def test_phone_book_edition(self):
        old_title = "Alte Behörder"
        old_phone_number = "069123321"
        instance = self.create_phone_book(title=old_title, phone_number=old_phone_number)
        self.assertEqual(PhoneBook.objects.count(), 1)
        self.assertEqual(instance.title, old_title)
        self.assertEqual(instance.phone_number, old_phone_number)

        with mixer.ctx(commit=False):
            new_title = "Neue Behörde"
            new_phone_number = "069444444"
            new_data = mixer.blend(PhoneBook, title=new_title, phone_number=new_phone_number).__dict__

        response = self.client.post(reverse_lazy("phonebook:edit", kwargs={"pk": instance.pk}), new_data)
        self.assertEqual(response.status_code, 302)
        instance.refresh_from_db()
        self.assertEqual(new_data.get("title"), new_title)
        self.assertEqual(new_data.get("phone_number"), new_phone_number)

    @staticmethod
    def create_phone_book(title=None, phone_number=None):
        with mixer.ctx(commit=False):
            data = mixer.blend(PhoneBook, title=title, phone_number=phone_number).__dict__
        form = PhoneBookForm(data=data)
        if form.is_valid() is True:
            instance = form.save()
            return instance
