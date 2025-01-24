# game/urls.py

from django.urls import path
from . import views
from . import local_game_views
from . import online_game_views
from . import local_tournament_views

urlpatterns = [
    path('', views.index, name='index'),
    path('list_results/', views.list_results, name='list_results'),

    # views ne renvoyant pas de html
    path('ready-game/<uuid:game_id>/', views.ready_game, name='ready_game'),
    
    path('<uuid:game_id>/', local_game_views.live_local_game, name='live_local_game'),
    path('parameter_local_game/', local_game_views.parameter_local_game, name='parameter_local_game'),
    
    path('tournament/parameter_local_tournament/', local_tournament_views.parameter_local_tournament, name='parameter_local_tournament'),
    path('tournament/<uuid:game_id>/', local_tournament_views.game, name='live_tournament_game'),
    path('tournament/<uuid:tournament_id>/', local_tournament_views.detail_local_tournament, name='bracket_tournament'),
    path('tournament/<uuid:tournament_id>/<str:match_type>/next_game_presentation_tournament/', local_tournament_views.next_game_presentation_tournament, name='next_game_presentation_tournament'),
    path('tournament/<uuid:tournament_id>/<str:match_type>/start_next_tournament_game/', local_tournament_views.start_next_tournament_game, name='start_next_tournament_game'),
    
]
