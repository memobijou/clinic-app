import os

from django.db.models import F

from account.models import Profile, Group
from pyfcm import FCMNotification
from pyfcm.errors import AuthenticationError, FCMServerError, InvalidDataError, InternalPackageError
from django.db import transaction
from messaging.models import ChatPushHistory


def send_push_notification_to_receiver(message, sender, receiver):
    print(os.environ.get("firebase_token"))
    if os.environ.get("firebase_token"):
        push_service = FCMNotification(api_key=os.environ.get("firebase_token"))
        try:
            chat_push_history, created = ChatPushHistory.objects.update_or_create(user=receiver, participant=sender)

            chat_push_history.unread_notifications += 1
            chat_push_history.save()

            registration_id = receiver.profile.device_token

            data_message = {
                "click_action": "FLUTTER_NOTIFICATION_CLICK",
                "id": "1",
                "status": "done",
                "category": "messaging",
                "sender": sender.id, "receiver": receiver.id
            }

            extra_notification_kwargs = {
                "options": {
                    "mutableContent": True,
                    "contentAvailable": True,
                    "apnsPushType": "background"
                },
                "apnsPushType": "background"
            }

            if len(message) > 20:
                message = message[:20] + "..."

            push_service.notify_single_device(
                registration_id=registration_id, message_title=sender, message_body=message, sound="default",
                data_message=data_message, badge=receiver.get_total_badges(), low_priority=False,
                extra_notification_kwargs=extra_notification_kwargs, content_available=True
            )

        except (AuthenticationError, FCMServerError, InvalidDataError, InternalPackageError) as e:
            print(e)


@transaction.atomic
def send_push_notification_to_group(message, sender, group: Group):
    print(os.environ.get("firebase_token"))
    if os.environ.get("firebase_token"):
        push_service = FCMNotification(api_key=os.environ.get("firebase_token"))
        try:
            receivers = group.users.exclude(id=sender.id)

            for receiver in receivers:
                chat_push_history, created = ChatPushHistory.objects.update_or_create(user=receiver, group=group)
                chat_push_history.unread_notifications += 1
                chat_push_history.save()

            for receiver in receivers:
                if len(message) > 20:
                    message = message[:20] + "..."

                registration_id = receiver.profile.device_token

                data_message = {
                    "click_action": "FLUTTER_NOTIFICATION_CLICK",
                    "id": "1",
                    "status": "done",
                    "category": "messaging-group",
                    "sender": sender.id, "receiver": receiver.id, "group": group.id
                }

                extra_notification_kwargs = {
                    "options": {
                        "mutableContent": True,
                        "contentAvailable": True,
                        "apnsPushType": "background"
                    },
                    "apnsPushType": "background"
                }

                if len(message) > 20:
                    message = message[:20] + "..."

                push_service.notify_single_device(
                    registration_id=registration_id, message_title=sender, message_body=message, sound="default",
                    data_message=data_message, badge=receiver.get_total_badges(), low_priority=False,
                    extra_notification_kwargs=extra_notification_kwargs, content_available=True
                )

        except (AuthenticationError, FCMServerError, InvalidDataError, InternalPackageError) as e:
            print(e)
