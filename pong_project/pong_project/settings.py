"""
Django settings for pong_project project.

Generated by 'django-admin startproject' using Django 5.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path
from datetime import timedelta

# ------------------------------------------------------------------
# 1) Base Directory
# ------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------------
# 2) Clés de sécurité & Debug
# ------------------------------------------------------------------
SECRET_KEY = 'django-insecure-%s7coj5xib2ic$tx*$k6$@7gtf7d^rd$lk0jbe-qjy@=e-s6#v'
DEBUG = False  # À mettre sur False en production

# ------------------------------------------------------------------
# 3) Hôtes autorisés
# ------------------------------------------------------------------
ALLOWED_HOSTS = ['*'] 
# En production, remplace '*' par l'IP ou le domaine, ex: ['192.168.1.138', 'example.com']

# ------------------------------------------------------------------
# 4) Authentification utilisateur
# ------------------------------------------------------------------
AUTH_USER_MODEL = 'accounts.CustomUser'


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,  # Le mot de passe doit comporter au moins 8 caractères
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ------------------------------------------------------------------
# 5) Internationalisation & Localisation
# ------------------------------------------------------------------
LANGUAGE_CODE = 'fr'

LANGUAGES = [
    ('fr', 'Français'),
    ('en', 'English'),
    ('es', 'Español'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',  # Assure-toi que le dossier existe
]

TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True
USE_TZ = True

# ------------------------------------------------------------------
# 6) Applications installées
# ------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'widget_tweaks',
    'channels',

    'accounts',
    'core',
    'game',
]

# ------------------------------------------------------------------
# 7) Middlewares
# ------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Gère les langues
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pong_project.middleware.JWTAuthenticationMiddleware',  # [TAGS] <JWT_tokens>
]

# ------------------------------------------------------------------
# 8) URL configuration
# ------------------------------------------------------------------
ROOT_URLCONF = 'pong_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),  # Répertoire global des templates
        ],
        'APP_DIRS': True,  # Permet de chercher les templates dans chaque app
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',  # Ajout pour la gestion des langues
            ],
        },
    },
]

WSGI_APPLICATION = 'pong_project.wsgi.application'
ASGI_APPLICATION = 'pong_project.asgi.application'  # Channels

# ------------------------------------------------------------------
# 9) Sécurité & HTTPS (Nginx en reverse proxy)
# ------------------------------------------------------------------
# Indique à Django que HTTPS est géré par un proxy (Nginx).
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Laisse Nginx gérer la redirection HTTP->HTTPS pour éviter les boucles
SECURE_SSL_REDIRECT = False

# Cookies uniquement envoyés via HTTPS (en prod).
SESSION_COOKIE_SECURE = True  # True en production
CSRF_COOKIE_SECURE = True     # True en production

# HSTS (Strict-Transport-Security) - Recommandé en production si toujours HTTPS
SECURE_HSTS_SECONDS = 31536000         # 31536000 (1 an) en production
#Optionnel, si tu veux forcer aussi les sous-domaines et éventuellement précharger ton domaine dans la liste HSTS des navigateurs (requires hstspreload.org).
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
# ------------------------------------------------------------------
# 10) CSRF
# ------------------------------------------------------------------
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8080',
    'http://192.168.1.138:8080',
    'http://192.168.1.138:443',
    'https://192.168.1.176:443',
    'https://10.12.6.7:8443',
    'https://10.12.5.6:8443',
    'https://192.168.1.138:8443',

    # 'https://votre-domaine.com',  # Ajoutez votre domaine en production
]
CSRF_COOKIE_SAMESITE = 'Lax'
# CSRF_COOKIE_SECURE = True (activé plus haut si besoin)

# ------------------------------------------------------------------
# 11) Base de données (PostgreSQL)
# ------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'pong_db'),
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.environ.get('POSTGRES_HOST', 'db'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}

# ------------------------------------------------------------------
# 12) Moteur de sessions
# ------------------------------------------------------------------
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_HTTPONLY = True

# ------------------------------------------------------------------
# 13) Cache (Redis) & Channels
# ------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"redis://{os.environ.get('REDIS_HOST','redis')}:{os.environ.get('REDIS_PORT','6379')}/1",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient'
        }
    }
}

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],
        },
    },
}

# ------------------------------------------------------------------
# 14) Gestion des fichiers statiques & médias
# ------------------------------------------------------------------
STATIC_URL = 'static/'

# Chemin où collectstatic place ses fichiers (ex: pour la prod)
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ------------------------------------------------------------------
# 15) Autres
# ------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# utilisé pour redirection pour anonymous user
LOGIN_URL = '/home/'