from phonebook.models import PhoneBook
from uniklinik.forms import BootstrapModelFormMixin


class PhoneBookForm(BootstrapModelFormMixin):
    class Meta:
        model = PhoneBook
        fields = ("last_name", "first_name", "title", "phone_number", "mobile_number", )
