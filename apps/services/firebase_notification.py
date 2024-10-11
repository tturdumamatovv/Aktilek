from datetime import date, datetime

import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging

cred = credentials.Certificate(
    {
        "type": "service_account",
        "project_id": "chat-a42dd",
        "private_key_id": "02a565503773f3ed6b1f321b5f14b44517177779",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCouQ2kJtqrmKJE\n71kbuBt+zD+pO2qwwYateXN2x5gUIZ6YPDRVBuCZmhNevdxd17mpnRHPnWou52oO\nQby75WnbRDpnd47jnmlRxMC+IHe/UVPgtWKA8qkdDCvr0iOykQWrpNqaHWIA/Vei\nD0CchtxH+Ps3a/0LHv9w90/6+h/aVbfsne9q8g0ZgYJZblKdP7S71yIso3LRlsBe\n0+dA+Kzw1LcucwkQNOXng+pCEgY76/58flNAlZlYQgaJd4J7v4hhZ/g+o4aeoLHj\ntL1Ki02XBzNtUVmCfCOkFBYcl/2H4oej9F3p7qcEUG9DdS4KF70tYOm459CV+sTT\nhZc37uixAgMBAAECggEAPMkmw/wHjgjYdVNx3A2xQjZdvR+d6X5fggIeei2geag/\nFgOiqvtmUZBz6A8o5FpDFntzHkRNLAbNa8N9NoiJYaisDfjB7vl0YjQraJQT8EZh\nnLRcf65tBP0MmdJEcCHVVCh5ZUqus0KSnt013u6rT/bAsw/hw27wgodnNjmE3kir\nn5zBvPdPChrV32qJDu3rzyhL342KW8K7X8gmppcJVljCO9LfgGKkVBXE9EFQKSNQ\nAr4AHQqomAnmVSKpLXiatHFKFsavogVa6V7aG6IjTXmwbGkc8WIwhnrF/GZEZ92T\n/FQ5DLo2q3xfUssQoSOJiicJUmUs7qdI+cj14ar/vQKBgQDasGWPJnKy8LDkGtJ/\n+1mHtzOWH5qi/REseszVhtgi5uwjQKgrQ0iRPsGojvzH+EHlwWgwgE1YwpdP/R19\n4pq4+Ku0zT2PBj1N50nQyVE22D2kI6FumwiuZrruESRAMEBQ7NlebFZqZgbkMQDX\nmeDgj+huhaev0ytZnZXjlPwyWwKBgQDFgk0oOedoG+98mQ01HqmzI0dBlkBbwktz\nOlPUKqy16ewgu5zWPZL+DZTOCxlFp2jQGNGlVijFF8rCWvFf4QU8Nk60vtDFcQUE\n3lqwBUYdH/I7DVfn7YsCN1adP86tThIhcYcJ2HvTTGetJeE78rj2mM1ZttQZ/0al\nWM5i+Rpm4wKBgA8UULxxM0GBdUEVVGR8yWyhRk5YuYn5l0CQ6yTiGm81qxy3LaFm\nD0/smt/rlCSZyrlz/6IwhqTTLinW0zzF7lNI2lYqPM9q57lCdIWQDCiS+pUh29TL\nneqgrM0To4NFkHnECy0GnWLSzDDZ7CvxsV7qrWVJlAl8ryWLxzUdJdK3AoGBAI0+\nQJU6y3zNNXeiMCrDsdH0sZl6rK2yBajylk5M8lPpZD6ITIF9aSgbaEXs8/a24KKo\njQwy0FcaS5qv1JufXNIReDmTl9MKnu87YBkuvFRJqz2Frk6itl0wW9V6cv/Gq/qU\nqGBnGy4hHqdZRnhLfPCEl53HvGiXANtv5bArujDHAoGAZ7XobTviodgwdyM47Afw\nZhnAFNawEsAjMm1Nup1ozJ+y/XSKOlO3XaUKI9++72CxWDch+DKoyUQ3kv+fQMnz\nVWpd2f/HAQJq0pwWA3KsUsxGiZiy29oPzU0OXlxeiR6/VSgf2v2fihyINPlaQG8b\nhrV10aJhH9De5Y7Wfhkavjc=\n-----END PRIVATE KEY-----\n",
        "client_email": "firebase-adminsdk-c5ft9@chat-a42dd.iam.gserviceaccount.com",
        "client_id": "111098542095254002536",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-c5ft9%40chat-a42dd.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }
)

firebase_admin.initialize_app(cred)


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
