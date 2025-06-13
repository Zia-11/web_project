import time
import logging

# создаём логгер для текущего модуля
logger = logging.getLogger(__name__)

# Middleware-класс для логирования каждого HTTP-запроса и времени его обработки
class LoggingMiddleware:

    # конструктор класса - получает функцию get_response, которая обрабатывает запрос
    def __init__(self, get_response):
        self.get_response = get_response

    #  основной метод  - логирует данные о входящем запросе, замеряет время обработки, логирует ответ
    def __call__(self, request):
        start = time.time()
        user = request.user.username if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous'
        logger.info(f"[REQUEST] {request.method} {request.get_full_path()} by {user}")
        
        response = self.get_response(request)
        
        duration = (time.time() - start) * 1000
        logger.info(f"[RESPONSE] {request.method} {request.get_full_path()} -> {response.status_code} in {duration:.1f}ms")
        return response
