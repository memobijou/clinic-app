from django.db import models, transaction
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from accomplishment.models import Accomplishment, UserAccomplishment


def get_name(self):
    return f"{self.first_name or ''} {self.last_name or ''}"


User.add_to_class("__str__", get_name)


class Group(models.Model):
    name = models.CharField(null=True, blank=False, max_length=200)
    users = models.ManyToManyField(User, blank=True, related_name="groups_list", verbose_name="Mitglieder")
    tasks = models.ManyToManyField("taskmanagement.Task", blank=True, related_name="groups_list")

    def __str__(self):
        return f"{self.name}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_admin = models.NullBooleanField(verbose_name="Administrations Status")
    device_token = models.CharField(max_length=500, null=True, blank=True)
    mentor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="students")
    biography = models.TextField(null=True, blank=True, verbose_name="Über dich")
    subject_area = models.ForeignKey("subject_area.SubjectArea", null=True, blank=True, on_delete=models.SET_NULL,
                                     related_name="profiles")

    @property
    def mentor_name(self):
        if hasattr(self.mentor, "profile"):
            return self.mentor.profile
        return "/"

    def get_students_string(self):
        students_string = ""
        for student in self.user.students.all():
            students_string += f"{str(student)}<br/>"
        if students_string == "":
            students_string = "/"
        return students_string

    def get_discipline(self):
        discipline = self.user.groups_list.filter(type="discipline").first()
        if discipline:
            return discipline.name

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        subject_area_changed = None
        if self.pk is not None:
            old_instance = Profile.objects.get(pk=self.pk)
            if old_instance.subject_area != self.subject_area:
                subject_area_changed = True

        if self.pk is None or subject_area_changed is True:
            accomplishments = Accomplishment.objects.filter(subject_areas__pk=self.subject_area_id).exclude(
                user_accomplishments__user__profile=self).distinct()
            UserAccomplishment.objects.bulk_create(
                [UserAccomplishment(accomplishment=accomplishment, user=self.user, score=0)
                 for accomplishment in accomplishments])
        return super().save(force_insert, force_update, using, update_fields)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created or hasattr(instance, "profile") is False:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
