from django.utils import translation
from channels.middleware import BaseMiddleware
from urllib.parse import urlparse


class LanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = request.META.get('HTTP_ACCEPT_LANGUAGE', 'ru').split(',')[0]
        translation.activate(lang)
        request.LANGUAGE_CODE = lang

        response = self.get_response(request)

        translation.deactivate()

        return response


class SimpleCorsMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        # Continue with the connection only if it's a WebSocket type
        if scope['type'] == 'websocket':
            headers = dict(scope['headers'])

            # If 'origin' header is present, manage CORS for WebSocket
            if b'origin' in headers:
                origin = headers[b'origin'].decode('utf-8')
                parsed_url = urlparse(origin)
                # Modify the scope to include the CORS headers
                scope['headers'].extend([
                    (b'access-control-allow-origin', bytes(origin, 'utf-8')),
                    (b'access-control-allow-credentials', b'true')
                ])
        return await super().__call__(scope, receive, send)
