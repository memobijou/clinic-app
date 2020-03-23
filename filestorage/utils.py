from pyfcm import FCMNotification
from pyfcm.errors import AuthenticationError, FCMServerError, InvalidDataError, InternalPackageError
import os
from account.models import Profile, User
from django.db.models import F


def send_push_notifications(users, title, message, category):
    if os.environ.get("firebase_token"):
        push_service = FCMNotification(api_key=os.environ.get("firebase_token"))
        registration_ids = []
        badges_totals = {}
        users = users.prefetch_related("profile")
        push_user_ids = []

        for user in users:
            if user.profile.device_token is not None:
                registration_ids.append(user.profile.device_token)
                push_user_ids.append(user.id)

        # Profile.objects.filter(user_id__in=push_user_ids).update(filestorage_badges=F("filestorage_badges") + 1)

        for user in User.objects.filter(id__in=push_user_ids):
            user_profile = user.profile
            if user_profile.device_token is not None:
                badges_totals[user_profile.device_token] = user_profile.get_total_badges()

        if len(registration_ids) > 0:
            try:
                if len(message) > 20:
                    message = message[:20] + "..."

                for registration_id in registration_ids:
                    push_service.notify_single_device(
                        registration_id=registration_id, message_title=title, message_body=message, sound="default",
                        data_message={"category": category}, badge=badges_totals.get(registration_id)
                    )

                # silent push
                push_service.notify_multiple_devices(
                    registration_ids=registration_ids,
                    data_message={"category": category}, content_available=True
                )
            except (AuthenticationError, FCMServerError, InvalidDataError, InternalPackageError) as e:
                print(e)
