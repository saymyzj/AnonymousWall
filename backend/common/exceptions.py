from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        detail = response.data
        if isinstance(detail, dict) and 'detail' in detail:
            message = str(detail['detail'])
        elif isinstance(detail, list):
            message = str(detail[0]) if detail else 'Error'
        elif isinstance(detail, dict):
            messages = []
            for field, errors in detail.items():
                if isinstance(errors, list):
                    messages.append(f"{field}: {errors[0]}")
                else:
                    messages.append(f"{field}: {errors}")
            message = '; '.join(messages)
        else:
            message = str(detail)

        response.data = {
            'code': response.status_code,
            'message': message,
            'data': None,
        }

    return response


class APIResponse(Response):
    def __init__(self, data=None, message='success', code=0, status_code=status.HTTP_200_OK, **kwargs):
        resp = {
            'code': code,
            'message': message,
            'data': data,
        }
        super().__init__(data=resp, status=status_code, **kwargs)
