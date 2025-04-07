import time
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)

class PerformanceMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        # Calculate request processing time
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            if duration > 0.5:  # Log requests taking more than 500ms
                logger.warning(f"Slow request: {request.path} took {duration:.2f} seconds")
        return response