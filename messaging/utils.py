import os

from django.db.models import F

from account.models import Profile
from pyfcm import FCMNotification
from pyfcm.errors import AuthenticationError, FCMServerError, InvalidDataError, InternalPackageError


def send_push_notification_to_receiver(message, sender, receiver):
    print(os.environ.get("firebase_token"))
    if os.environ.get("firebase_token"):
        push_service = FCMNotification(api_key=os.environ.get("firebase_token"))
        try:
            Profile.objects.filter(user=receiver).update(messaging_badges=F("messaging_badges") + 1)
            if len(message) > 20:
                message = message[:20] + "..."
            r = push_service.notify_single_device(
                registration_id=receiver.profile.device_token, message_title=f"{sender}",
                message_body=message,
                sound="default", data_message={"category": "messaging"}, badge=receiver.profile.get_total_badges())
            receiver.profile.messaging_badges += 1
            receiver.profile.save()
            print(f"he: {r}")
            print("success chat")
        except (AuthenticationError, FCMServerError, InvalidDataError, InternalPackageError) as e:
            print(e)
