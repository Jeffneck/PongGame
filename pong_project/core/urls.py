from django.urls import path
from .views import get_navbar, home_view, landing_view, not_found_view
from django.views.generic import TemplateView


app_name = 'core'

urlpatterns = [
    # Route pour la barre de navigation
    path('navbar/', get_navbar, name='navbar'),
    
    # Route pour la page d'accueil
    path('home/', home_view, name='home_view'),
    path('404/', not_found_view, name='404'),
    # Route pour la page de destination
    path('', landing_view, name='landing_view'),
]
