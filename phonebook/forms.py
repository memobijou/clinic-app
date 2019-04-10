from phonebook.models import PhoneBook
from uniklinik.forms import BootstrapModelFormMixin


class PhoneBookForm(BootstrapModelFormMixin):
    class Meta:
        model = PhoneBook
        fields = ("title", "phone_number", )
