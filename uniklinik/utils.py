from django.contrib.auth.models import User
from django.db.models import F
from pyfcm import FCMNotification
from pyfcm.errors import AuthenticationError, FCMServerError, InvalidDataError, InternalPackageError
import os


def send_push_notifications(users, title, message, category, update_badge_method):
    registration_ids = []
    badges_totals = {}
    registration_id_profiles = {}
    users = users.prefetch_related("profile")
    push_user_ids = []

    for user in users:
        profile = user.profile

        if profile.device_token is not None:
            registration_ids.append(user.profile.device_token)
            push_user_ids.append(user.id)

            registration_id_profiles[profile.device_token] = profile

    print(f"crazy man: {push_user_ids}")

    update_badge_method(push_user_ids)

    if os.environ.get("firebase_token"):
        push_service = FCMNotification(api_key=os.environ.get("firebase_token"))

        for user in User.objects.filter(id__in=push_user_ids):
            if user.profile.device_token is not None:
                badges_totals[user.profile.device_token] = user.profile.get_total_badges()

        data_message = {
            "click_action": "FLUTTER_NOTIFICATION_CLICK",
            "id": "1",
            "status": "done",
            "category": category
        }

        extra_notification_kwargs = {
            "options": {
                "mutableContent": True,
                "contentAvailable": True,
                "apnsPushType": "background"
            },
            "apnsPushType": "background"
        }

        if len(registration_ids) > 0:
            try:
                if len(message) > 20:
                    message = message[:20] + "..."

                for registration_id in registration_ids:
                    if registration_id_profiles[registration_id].is_android is True:
                        push_service.notify_single_device(
                            registration_id=registration_id, message_title=title, message_body=message, sound="default",
                            data_message=data_message, badge=badges_totals.get(registration_id), low_priority=False,
                            extra_notification_kwargs=extra_notification_kwargs, content_available=True
                        )
                        push_service.notify_single_device(
                            registration_id=registration_id, data_message=data_message,
                            low_priority=False,
                            extra_notification_kwargs=extra_notification_kwargs, content_available=True
                        )
                    else:
                        push_service.notify_single_device(
                            registration_id=registration_id, message_title=title, message_body=message, sound="default",
                            data_message=data_message, badge=badges_totals.get(registration_id), low_priority=False,
                            extra_notification_kwargs=extra_notification_kwargs, content_available=True
                        )

                # silent push
                # push_service.notify_multiple_devices(
                #     registration_ids=registration_ids,
                #     data_message=data_message, content_available=True, click_action="FLUTTER_NOTIFICATION_CLICK",
                #     low_priority=False, extra_notification_kwargs=extra_notification_kwargs
                # )
            except (AuthenticationError, FCMServerError, InvalidDataError, InternalPackageError) as e:
                print(e)
