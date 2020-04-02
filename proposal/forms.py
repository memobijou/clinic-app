from uniklinik.forms import BootstrapModelFormMixin
from proposal.models import Type, Proposal
from uniklinik.utils import send_push_notifications
from django.contrib.auth.models import User
from account.models import Profile
from django.db.models import F


class TypeForm(BootstrapModelFormMixin):
    class Meta:
        model = Type
        fields = ("title",)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['title'].required = True
        self.fields['title'].widget.attrs['required'] = 'required'


class ProposalForm(BootstrapModelFormMixin):
    class Meta:
        model = Proposal
        fields = ("confirmed", )

    def save(self, commit=True):
        if self.instance.user:

            def update_badge_method(push_user_ids):
                Profile.objects.filter(user_id__in=push_user_ids).update(proposal_badges=F("proposal_badges") + 1)

            start_date_formatted = f"{self.instance.start_date.day}.{self.instance.start_date.month}." \
                f"{self.instance.start_date.year}"

            end_date_formatted = f"{self.instance.end_date.day}.{self.instance.end_date.month}." \
                f"{self.instance.end_date.year}"

            push_message = f'{self.instance.type.title}: {start_date_formatted}-{end_date_formatted}'

            user_queryset = User.objects.filter(pk=self.instance.user.pk)
            print(f"braaaaaaaa: {user_queryset}")
            if self.instance.confirmed is True:
                send_push_notifications(user_queryset, "Ihr Antrag wurde genehmigt", push_message, "proposal",
                                        update_badge_method)
            elif self.instance.confirmed is False:
                send_push_notifications(user_queryset, "Ihr Antrag wurde abgelehnt", push_message, "proposal",
                                        update_badge_method)
            else:
                pass
        return super().save(commit)
