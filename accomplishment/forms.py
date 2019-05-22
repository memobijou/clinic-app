from accomplishment.models import Accomplishment, UserAccomplishment
from subject_area.models import SubjectArea
from uniklinik.forms import BootstrapModelFormMixin
from django.db import transaction
from django import forms
from django.contrib.auth.models import User


class AccomplishmentFormMixin(BootstrapModelFormMixin):
    subject_areas = forms.ModelMultipleChoiceField(
        queryset=SubjectArea.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)

    class Meta:
        model = Accomplishment
        fields = ("name", "full_score", "subject_areas",)

    def clean_full_score(self):
        full_score = self.cleaned_data['full_score']
        if full_score <= 0:
            self.add_error("full_score", "Gesamtpunktezahl muss größer als 0 sein")
        return full_score

    @transaction.atomic
    def save(self, commit=True, **kwargs):
        is_new_object = False

        if self.instance.pk is None:
            is_new_object = True

        instance = super().save(commit)
        users = User.objects.filter(profile__subject_area__in=instance.subject_areas.all()).distinct()

        # Das muss zu Fachrichtungen gemacht werden statt zu Gruppen
        if is_new_object is False:
            existing_users = UserAccomplishment.objects.filter(
                user__in=users, accomplishment=self.instance).values_list("user__pk", flat=True).distinct()
            users = users.exclude(pk__in=existing_users)

        UserAccomplishment.objects.bulk_create(
           [UserAccomplishment(user=user, accomplishment=instance, score=0) for user in users])
        return instance
