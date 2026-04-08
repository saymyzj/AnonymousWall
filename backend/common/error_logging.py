import logging
import traceback

from django.http import JsonResponse
from django.conf import settings


logger = logging.getLogger(__name__)


class ApiExceptionLoggingMiddleware:
    """
    Print unhandled exceptions to stdout/stderr so they are visible in
    Function Compute logs, and keep API responses in JSON format.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            response['X-App-Build'] = getattr(settings, 'APP_BUILD_MARKER', 'unknown')
            response['X-App-Middleware'] = 'api-exception-logging-v1'
            return response
        except Exception as exc:  # noqa: BLE001
            logger.exception('Unhandled exception for %s %s', request.method, request.path)
            traceback.print_exc()

            if request.path.startswith('/api/'):
                response = JsonResponse(
                    {
                        'code': 500,
                        'message': f'服务器内部错误: {exc.__class__.__name__}',
                        'data': None,
                    },
                    status=500,
                )
                response['X-App-Build'] = getattr(settings, 'APP_BUILD_MARKER', 'unknown')
                response['X-App-Middleware'] = 'api-exception-logging-v1'
                return response
            raise
