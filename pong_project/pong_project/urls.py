"""
URL configuration for pong_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.conf.urls.i18n import i18n_patterns

import logging

from core.views import landing_view  # Import direct de la view

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

logger.debug("Entrée dans urls.py de l'app Transcendence")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('game/', include('game.urls', namespace='game')),
    path('core/', include('core.urls', namespace='core')),
    # Supprimez ou commentez cette ligne si elle interfère avec la route de fallback
    # path('', include(('core.urls', 'core'), namespace='landing')),.
]


# Route de fallback pour servir landing.html pour toutes les autres URLs
urlpatterns += [
    re_path(r'^.*$', TemplateView.as_view(template_name='landing.html')),
    path('i18n/', include('django.conf.urls.i18n')),
]
