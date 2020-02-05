from phonebook.models import PhoneBook, Category
from uniklinik.forms import BootstrapModelFormMixin


class PhoneBookForm(BootstrapModelFormMixin):
    class Meta:
        model = PhoneBook
        fields = ("last_name", "first_name", "title", "phone_number", "mobile_number", "category",)


class CategoryForm(BootstrapModelFormMixin):
    class Meta:
        model = Category
        fields = ("title",)
