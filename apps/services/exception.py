from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None and isinstance(response.data, dict):
        if 'error' in response.data:
            # If 'error' contains a list, flatten it into a single string
            if isinstance(response.data['error'], list):
                response.data['error'] = response.data['error'][0]

        # Handle other cases like 'non_field_errors' or 'detail'
        if 'non_field_errors' in response.data:
            response.data = {"error": response.data['non_field_errors'][0]}
        elif 'detail' in response.data:
            response.data = {"error": response.data['detail']}

    return response