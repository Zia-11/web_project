import time
import logging

logger = logging.getLogger(__name__)

class LoggingMiddleware:
    # логирует каждый запрос и замеряет время обработки
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        user = request.user.username if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous'
        logger.info(f"[REQUEST] {request.method} {request.get_full_path()} by {user}")
        
        response = self.get_response(request)
        
        duration = (time.time() - start) * 1000
        logger.info(f"[RESPONSE] {request.method} {request.get_full_path()} -> {response.status_code} in {duration:.1f}ms")
        return response
