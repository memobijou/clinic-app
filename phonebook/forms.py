from phonebook.models import PhoneBook, Category
from uniklinik.forms import BootstrapModelFormMixin
from uniklinik.utils import send_push_notifications
from django.contrib.auth.models import User
from account.models import Profile
from django.db.models import F


class PhoneBookForm(BootstrapModelFormMixin):
    class Meta:
        model = PhoneBook
        fields = ("last_name", "first_name", "title", "phone_number", "mobile_number", "category",)

    def save(self, commit=True):
        first_name = self.cleaned_data.get("first_name", "")
        last_name = self.cleaned_data.get("last_name", "")
        title = self.cleaned_data.get("title")

        message = ""
        if title:
            message = title
        else:
            if first_name or last_name:
                message = f"{first_name} {last_name}"

        def update_badge_method(push_user_ids):
            Profile.objects.filter(user_id__in=push_user_ids).update(
                phonebook_badges=F("phonebook_badges") + 1)

        # send_push_notifications(User.objects.all(), f"Neuer Kontakt", message, "phonebook", update_badge_method)
        return super().save(commit)


class CategoryForm(BootstrapModelFormMixin):
    class Meta:
        model = Category
        fields = ("title",)
