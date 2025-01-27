# game/urls.py

# from django.urls import path
# from . import views
# from . import local_game_views
# from . import online_game_views
# from . import local_tournament_views

# urlpatterns = [
#     path('', views.index, name='index'),
#     path('list_results/', views.list_results, name='list_results'),

#     # Views ne renvoyant pas de HTML
#     path('ready-game/<uuid:game_id>/', views.ready_game, name='ready_game'),
    
#     path('local_game/<uuid:game_id>/', local_game_views.live_local_game, name='live_local_game'),
#     path('local_game/parameter_local_game/', local_game_views.parameter_local_game, name='parameter_local_game'),
    
#     path('tournament/parameter_local_tournament/', local_tournament_views.parameter_local_tournament, name='parameter_local_tournament'),
    
#     # Routes modifiées avec segments distinctifs
#     path('tournament/live/<uuid:game_id>/', local_tournament_views.live_tournament_game, name='live_tournament_game'),
#     path('tournament/detail/<uuid:tournament_id>/', local_tournament_views.detail_local_tournament, name='detail_local_tournament'),
    
#     path('tournament/detail/<uuid:tournament_id>/<str:match_type>/next_game_presentation_tournament/', local_tournament_views.next_game_presentation_tournament, name='next_game_presentation_tournament'),
#     path('tournament/detail/<uuid:tournament_id>/<str:match_type>/start_next_tournament_game/', local_tournament_views.start_next_tournament_game, name='start_next_tournament_game'),
# ]


from django.urls import path

from .views.gameHome import GameHomeView
from .views.gameMenu import GameMenuView, CreateGameLocalView
from .views.gameLoading import LoadingView
from .views.gameSelectTournament import SelectTournamentView
from .views.gameInvitation import InviteGameView
from .views.gameInvitation import SendInvitationView, CancelInvitationView, RespondToInvitationView, ListInvitationsView, AcceptGameInvitationView

import logging


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

logger.debug("Rentre dans urls.py de l'app game")

app_name = 'game'

urlpatterns = [
    path('home/', GameHomeView.as_view(), name='home'),  # Mise à jour pour CBV
    path('menu/', GameMenuView.as_view(), name='game_menu'),  # Mise à jour pour CBV
    path('loading/', LoadingView.as_view(), name='loading'),  # Mise à jour pour CBV
    path('select_tournament/', SelectTournamentView.as_view(), name='select_tournament'),  # Mise à jour pour CBV
    path('invite_game/', InviteGameView.as_view(), name='invite_game'),  # Vue fonctionnelle
    # path('invite_tournament/', invite_tournament_view, name='invite_tournament'),  # Vue fonctionnelle
    path('send_invitation/', SendInvitationView.as_view(), name='send_invitation'),
    path('cancel_invitation/', CancelInvitationView.as_view(), name='cancel_invitation'),  # Vue fonctionnelle
    path('respond_to_invitation/', RespondToInvitationView.as_view(), name='respond_to_invitation'),
    path('create_local_game/', CreateGameLocalView.as_view(), name='create_local_game'),
    path('accept_invitation/<int:invitation_id>/', AcceptGameInvitationView.as_view(), name='accept_invitation'),
    path('respond_to_invitation/', RespondToInvitationView.as_view(), name='respond_to_invitation'),
    path('list_invitations/', ListInvitationsView.as_view(), name='list_invitations'),

]
