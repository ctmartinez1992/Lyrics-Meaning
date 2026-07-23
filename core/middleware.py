import logging


logger = logging.getLogger("core.request")


class RequestFailureLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code >= 500:
            logger.error(
                "request_failed method=%s path=%s status=%s",
                request.method,
                request.path,
                response.status_code,
            )
        return response

    def process_exception(self, request, exception):
        logger.exception(
            "request_exception method=%s path=%s error=%s",
            request.method,
            request.path,
            exception,
        )
        return None

