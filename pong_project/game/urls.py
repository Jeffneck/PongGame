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
from .views.gameMenu import GameMenuView
from .views.gameLoading import LoadingView
from .views.gameLocal import StartLocalGameView, CreateGameLocalView
from .views.gameResults import GameResultsView 
from .views.gameStatus import GetGameStatusView 
from .views.gameOnline import CreateGameOnlineView, SendGameSessionInvitationView, AcceptGameInvitationView, RejectGameInvitationView, CleanExpiredInvitationsView, CheckGameInvitationStatusView, StartOnlineGameView, JoinOnlineGameAsLeftView, JoinOnlineGameAsRightView
from .views.gameTournament import CreateTournamentView, CreateTournamentGameSessionView, StartTournamentGameSessionView, TournamentBracketView, TournamentNextGameView
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

logger.debug("Rentre dans urls.py de l'app game")

app_name = 'game'

urlpatterns = [
    path('home/', GameHomeView.as_view(), name='home'),  # Mise à jour pour CBV
    path('menu/', GameMenuView.as_view(), name='game_menu'),  # Mise à jour pour CBV
    path('loading/', LoadingView.as_view(), name='loading'),  # Mise à jour pour CBV
    # path('invite_game/', InviteGameView.as_view(), name='invite_game'),  # Vue fonctionnelle
    # path('invite_tournament/', invite_tournament_view, name='invite_tournament'),  # Vue fonctionnelle
    # path('send_invitation/', SendInvitationView.as_view(), name='send_invitation'),
    # path('cancel_invitation/', CancelInvitationView.as_view(), name='cancel_invitation'),  # Vue fonctionnelle
    # path('respond_to_invitation/', RespondToInvitationView.as_view(), name='respond_to_invitation'),
    # path('accept_invitation/<int:invitation_id>/', AcceptGameInvitationView.as_view(), name='accept_invitation'),
    # path('respond_to_invitation/', RespondToInvitationView.as_view(), name='respond_to_invitation'),
    # path('list_invitations/', ListInvitationsView.as_view(), name='list_invitations'),
    
    #LOCAL GAME 
    path('create_local_game/', CreateGameLocalView.as_view(), name='create_local_game'),
    path('start_local_game/<uuid:game_id>/', StartLocalGameView.as_view(), name='start_local_game'),

    # LOCAL TOURNAMENT GAMES
    path('create_tournament/', CreateTournamentView.as_view(), name='create_tournament'),
    path('tournament_bracket/<uuid:tournament_id>/', TournamentBracketView.as_view(), name='tournament_bracket'),
    path('tournament_next_game/<uuid:tournament_id>/', TournamentNextGameView.as_view(), name='tournament_next_game'),
    path('create_tournament_game_session/<uuid:tournament_id>/', CreateTournamentGameSessionView.as_view(), name='create_tournament_gameSession'),
    path('start_tournament_game_session/<uuid:game_id>/', StartTournamentGameSessionView.as_view(), name='start_tournament_gameSession'),

    #ONLINE GAME
    # create game
    # player left (the one that send the invitation)
    path('create_game_online/', CreateGameOnlineView.as_view(), name='create_game_online'),
    path('send_gameSession_invitation/', SendGameSessionInvitationView.as_view(), name='send_gameSession_invitation'),
    path('join_online_game_as_left/<uuid:game_id>/', JoinOnlineGameAsLeftView.as_view(), name='join_online_game_as_left'),
    path('start_online_game/<uuid:game_id>/', StartOnlineGameView.as_view(), name='start_online_game'),

    # player right (the one that receive the invitation)
    path('accept_game_invitation/<uuid:invitation_id>/', AcceptGameInvitationView.as_view(), name='accept_game_invitation'),
    path('join_online_game_as_right/<uuid:game_id>/', JoinOnlineGameAsRightView.as_view(), name='join_online_game_as_right'),
    path('reject_game_invitation/<uuid:invitation_id>/', RejectGameInvitationView.as_view(), name='reject_game_invitation'),

    # Invitations managers
    path('check_invitation_status/<uuid:invitation_id>/', CheckGameInvitationStatusView.as_view(), name='check_invitation_status'),
    path('clean_expired_invitations/<uuid:invitation_id>/', CleanExpiredInvitationsView.as_view(), name='clean_expired_invitations'),

    # See game results
    path('game_results/<uuid:game_id>/', GameResultsView.as_view(), name='get_local_results'),
    path('get_game_status/<uuid:game_id>/', GetGameStatusView.as_view(), name='get_game_status'),
]
