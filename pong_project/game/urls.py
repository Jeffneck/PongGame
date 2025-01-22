# game/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_game, name='create_game'),
    path('<uuid:game_id>/', views.game, name='game'),
    path('results/', views.list_results, name='list_results'),
    path('tournament/create/', views.create_local_tournament, name='create_local_tournament'),
    path('tournament/<uuid:tournament_id>/', views.detail_local_tournament, name='detail_local_tournament'),
    path('tournament/<uuid:tournament_id>/<str:match_type>/prepare/', views.prepare_game, name='prepare_game'),
    path('tournament/<uuid:tournament_id>/<str:match_type>/start/', views.start_game, name='start_game'),
]
