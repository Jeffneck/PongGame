from django.urls import path
from . import views

urlpatterns = [
    path('', views.game_page, name='game_page'),
    path('get_positions/', views.get_positions, name='get_positions'),
    path('update_position/', views.update_position, name='update_position'),
]