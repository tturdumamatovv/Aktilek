from datetime import date, datetime

import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging


def send_firebase_notification(token, title, body, data, image_url=None):
    data = {key: str(value) for key, value in data.items()}

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
            image=image_url or 'https://www.gstatic.com/webp/gallery/2.jpg'
        ),
        data=data,
        token=token,
    )
    response = messaging.send(message)
    return response
