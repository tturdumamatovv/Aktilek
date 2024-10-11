import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()  # Ensure Django is fully setup before importing channels and apps

from apps.orders.routing import ws_urlpatterns
from apps.support_admin_chat.routing import websocket_urlpatterns

from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from .middleware import SimpleCorsMiddleware  # Ensure you import the correct path

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        SimpleCorsMiddleware(  # Use your custom middleware here
            AuthMiddlewareStack(
                URLRouter(
                    ws_urlpatterns + websocket_urlpatterns,
                )
            )
        )
    ),
})
