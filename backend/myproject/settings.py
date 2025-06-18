from pathlib import Path
from decouple import config
import os

# корневая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# настройки хранения медиафайлов
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# безопасные настройки
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
DB_NAME = config('DB_NAME', default='db.sqlite3')

# настройка подключения к бд
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, DB_NAME),
    }
}

ALLOWED_HOSTS = []

# описание подключаемых приложений
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'accounts.apps.AccountsConfig',
    'drf_yasg',
    'core.apps.CoreConfig',
    'corsheaders',
    'channels',
]

# Middleware - промежуточные обработчики запросов
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.LoggingMiddleware',
]

# основной файл с роутингом
ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        # бэкенд шаблонов
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# настройка для запуска через WSGI
WSGI_APPLICATION = 'myproject.wsgi.application'

# валидация паролей пользователей
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# DRF
REST_FRAMEWORK = {
    # подключаем бэкенды фильтрации (django-filters), поиска и сортировки
    'DEFAULT_FILTER_BACKENDS': [
        # для точечной фильтрации по полям
        'django_filters.rest_framework.DjangoFilterBackend',
        # для поиска по вхождению
        'rest_framework.filters.SearchFilter',
        # для сортировки
        'rest_framework.filters.OrderingFilter',
    ],
    # подключаем пагинацию страниц
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 1000,

    # аутентификация: только по токену
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
        # 'rest_framework.authentication.BasicAuthentication',
    ],

    # права по умолчанию (все пользователи должны быть аутентифицированы)
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# настройки документации
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        # базовая авторизация
        'BasicAuth': {
            'type': 'basic',
            'description': 'HTTP Basic Authentication; введите свой username и password.',
        },
        # с токеном
        'TokenAuth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Для запросов поместите сюда ваш токен в формате: Token <ваш_токен>'
        }

    },
    'USE_SESSION_AUTH':  True,
    'LOGIN_URL': '/accounts/login/',
    'LOGOUT_URL': '/accounts/logout/',
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# логирование
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080"
]

# разрешить запросы с любых доменов
CORS_ALLOW_ALL_ORIGINS = True

# для channels
ASGI_APPLICATION = 'myproject.asgi.application'

# канальный слой для WebSocket
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}
