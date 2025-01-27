from django.urls import path
from .views import get_navbar, home_view, landing_view


app_name = 'core'

urlpatterns = [
    # Route pour la barre de navigation
    path('navbar/', get_navbar, name='navbar'),
    
    # Route pour la page d'accueil
    path('home/', home_view, name='home_view'),
    
    # Route pour la page de destination
    path('', landing_view, name='landing_view'),
]
