from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, m2m_changed, pre_save
from django.dispatch import receiver
from pyfcm import FCMNotification
from pyfcm.errors import AuthenticationError, FCMServerError, InvalidDataError, InternalPackageError
from accomplishment.models import Accomplishment, UserAccomplishment
from taskmanagement.models import UserTask
import os
import random


def get_name(self):
    profile = self.profile
    if profile and profile.title:
        return f"{profile.title} {self.first_name or ''} {self.last_name or ''}"
    else:
        return f"{self.first_name or ''} {self.last_name or ''}"


User.add_to_class("__str__", get_name)


def random_color():
    return "#" + "%06x" % random.randint(0, 0xFFFFFF)


class Group(models.Model):
    name = models.CharField(null=True, blank=False, max_length=200)
    users = models.ManyToManyField(User, blank=True, related_name="groups_list", verbose_name="Mitglieder")
    tasks = models.ManyToManyField("taskmanagement.Task", blank=True, related_name="groups_list")
    color = models.CharField(default=random_color, max_length=200, verbose_name="Farbe")

    def __str__(self):
        return f"{self.name}"


@receiver(m2m_changed, sender=Group.users.through)
def users_listener(sender, instance: Group, action, **kwargs):
    tasks = instance.tasks.all()
    new_group_users = instance.users.all()

    # HIER UNBEDINGT OPTIMIEREN WENN DATENSÄTZE MEHR WERDEN WIRD DAS SEHR LANGSAM

    bulk_instances = []
    for task in tasks:
        for user in new_group_users:
            if UserTask.objects.filter(task=task, user=user).exists() is False:
                bulk_instances.append(UserTask(task=task, user=user))
    print(f"QAF: {bulk_instances}")
    UserTask.objects.bulk_create(bulk_instances)


title_choices = ((None, "--------"), ("Dr.", "Dr"),)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_admin = models.NullBooleanField(verbose_name="Administrations Status")
    device_token = models.CharField(max_length=500, null=True, blank=True)
    mentor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="students")
    biography = models.TextField(null=True, blank=True, verbose_name="Über dich")
    subject_area = models.ForeignKey("subject_area.SubjectArea", null=True, blank=True, on_delete=models.SET_NULL,
                                     related_name="profiles")
    title = models.CharField(choices=title_choices, null=True, blank=True, max_length=200)
    confirmed = models.NullBooleanField()

    @property
    def mentor_name(self):
        if hasattr(self.mentor, "profile"):
            return self.mentor.profile
        return ""

    def get_students_string(self):
        students_string = ""
        for student in self.user.students.all():
            students_string += f"{str(student)}<br/>"
        if students_string == "":
            students_string = ""
        return students_string

    def get_discipline(self):
        discipline = self.user.groups_list.filter(type="discipline").first()
        if discipline:
            return discipline.name

    def __str__(self):
        if self.title:
            return f"{self.title} {self.user.first_name} {self.user.last_name}"
        else:
            return f"{self.user.first_name} {self.user.last_name}"

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        subject_area_changed = None
        mentor_changed = None

        if self.pk is not None:
            old_instance = Profile.objects.get(pk=self.pk)

            if old_instance.subject_area != self.subject_area:
                subject_area_changed = True
            if old_instance.mentor != self.mentor:
                mentor_changed = True

        if self.pk is None or subject_area_changed is True:
            accomplishments = Accomplishment.objects.filter(subject_areas__pk=self.subject_area_id).exclude(
                user_accomplishments__user__profile=self).distinct()
            UserAccomplishment.objects.bulk_create(
                [UserAccomplishment(accomplishment=accomplishment, user=self.user, score=0)
                 for accomplishment in accomplishments])

        if mentor_changed is True:
            self.send_push_notifcation_to_mentor_and_student(self.mentor, self)
        return super().save(force_insert, force_update, using, update_fields)

    @staticmethod
    def send_push_notifcation_to_mentor_and_student(mentor, student_profile):
        print(os.environ.get("firebase_token"))
        if os.environ.get("firebase_token"):
            push_service = FCMNotification(api_key=os.environ.get("firebase_token"))
            try:
                r = push_service.notify_single_device(
                    registration_id=student_profile.device_token, message_title=f"Neuer Mentor",
                    message_body=f"{mentor} wurde Ihnen als Mentor zugeteilt",
                    sound="default", data_message={"category": "mentor"})
                print(f"he: {r}")
                print("success student")
            except (AuthenticationError, FCMServerError, InvalidDataError, InternalPackageError) as e:
                print(e)

            try:
                if hasattr(mentor, "profile"):
                    r = push_service.notify_single_device(
                        registration_id=mentor.profile.device_token, message_title="Neuer Schüler",
                        message_body=f"{student_profile} wurde Ihnen als Schüler zugeteilt",
                        sound="default", data_message={"category": "mentor"})
                    print("success mentor")
                    print(f"he: {r}")
            except (AuthenticationError, FCMServerError, InvalidDataError, InternalPackageError) as e:
                print(e)


def send_push_notifcation_to_activated_user(user):
    print(os.environ.get("firebase_token"))
    if os.environ.get("firebase_token"):
        push_service = FCMNotification(api_key=os.environ.get("firebase_token"))
        try:
            r = push_service.notify_single_device(
                registration_id=user.profile.device_token, message_title=f"Herzlich Willkommen",
                message_body=f"Ihr Account wurde freigeschaltet",
                sound="default", data_message={"category": "registration-activation"})
            print(f"he: {r}")
            print("success acctivation")
        except (AuthenticationError, FCMServerError, InvalidDataError, InternalPackageError) as e:
            print(e)


@receiver(pre_save, sender=User)
def send_activation_notification(sender, instance, **kwargs):
    if instance.pk is not None:
        old_user = User.objects.get(pk=instance.pk)
        print(f"why: {old_user.is_active} --- {instance.is_active}")
        if old_user.is_active is not True and instance.is_active is True:
            print(f"love love")
            send_push_notifcation_to_activated_user(instance)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created or hasattr(instance, "profile") is False:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
