from django.http import JsonResponse
from functools import wraps

# проверка что пользователь состоит в группе с именем role_name
def role_required(role_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user

            # проверяем авторизован ли пользователь
            if not user.is_authenticated:
                return JsonResponse({'detail': 'Требуется аутентификация.'}, status=401)
            
            # проверяем состоит ли пользователь в группе с нужной ролью
            if not user.groups.filter(name=role_name).exists():
                return JsonResponse({'detail': f'Запрещено: требуется {role_name} роль.'}, status=403)
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
