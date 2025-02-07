# gameOnline.py
import logging
from django.views import View
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from pong_project.decorators import login_required_json
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils.timezone import now
from accounts.models import CustomUser
from game.models import GameSession, GameInvitation
from game.forms import GameParametersForm
from game.manager import schedule_game
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)

@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class CreateGameOnlineView(View):
    """
    Crée une session de jeu en ligne et renvoie la page d'invitation.
    """
    def post(self, request):
        try:
            form = GameParametersForm(request.POST)
            logger.debug("Entering CreateGameOnlineView")
            if not form.is_valid():
                logger.warning("Invalid game parameters: %s", form.errors)
                return JsonResponse({
                    'status': 'error',
                    'message': _("Paramètres invalides."),
                    'errors': form.errors
                }, status=400)
            
            session = GameSession.objects.create(
                status='waiting',
                is_online=True,
                player_left=request.user
            )
            parameters = form.save(commit=False)
            parameters.game_session = session
            parameters.save()
            
            logger.info(f"Online GameSession {session.id} created by {request.user.username}")
            friends = request.user.friends.all()
            if not friends.exists():
                return JsonResponse({
                    'status': 'error',
                    'message': _("Vous n'avez pas encore ajouté d'amis. Ajoutez des amis pour les inviter à jouer.")
                }, status=400)
            
            rendered_html = render_to_string(
                'game/online_game/invite_game.html',
                {'game_id': session.id, 'friends': friends},
                request=request
            )
            return JsonResponse({
                'status': 'success',
                'message': _("Partie en ligne créée avec succès."),
                'game_id': str(session.id),
                'html': rendered_html
            }, status=200)
        except Exception as e:
            logger.exception("Error in CreateGameOnlineView: %s", e)
            return JsonResponse({'status': 'error', 'message': _("Internal server error")}, status=500)

@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class SendGameSessionInvitationView(View):
    """
    Envoie une invitation pour une session de jeu en ligne.
    """
    def post(self, request):
        try:
            session_id = request.POST.get('session_id', '').strip()
            friend_username = request.POST.get('friend_username', '').strip()
            if not session_id or not friend_username:
                return JsonResponse({
                    'status': 'error',
                    'message': _("Données manquantes (session_id ou friend_username).")
                }, status=400)
            session = get_object_or_404(GameSession, id=session_id, is_online=True)
            if session.player_left != request.user:
                return JsonResponse({
                    'status': 'error',
                    'message': _("Vous n'êtes pas autorisé à inviter pour cette session.")
                }, status=403)
            try:
                friend = CustomUser.objects.get(username=friend_username)
            except CustomUser.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': _("Ami introuvable.")
                }, status=404)
            if friend == request.user:
                return JsonResponse({
                    'status': 'error',
                    'message': _("Vous ne pouvez pas vous inviter vous-même.")
                }, status=400)
            existing_invitation = GameInvitation.objects.filter(
                from_user=request.user,
                to_user=friend,
                session=session,
                status='pending'
            ).first()
            if existing_invitation:
                return JsonResponse({
                    'status': 'error',
                    'message': _("Une invitation est déjà en attente pour cette session.")
                }, status=400)
            invitation = GameInvitation.objects.create(
                from_user=request.user,
                to_user=friend,
                session=session,
                status='pending'
            )
            rendered_html = render_to_string('game/online_game/loading.html', request=request)
            return JsonResponse({
                'status': 'success',
                'html': rendered_html,
                'message': _("Invitation envoyée."),
                'invitation_id': invitation.id
            }, status=200)
        except Exception as e:
            logger.exception("Error in SendGameSessionInvitationView: %s", e)
            return JsonResponse({'status': 'error', 'message': _("Internal server error")}, status=500)

@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class AcceptGameInvitationView(View):
    """
    Le joueur destinataire accepte une invitation et démarre la session.
    """
    def post(self, request, invitation_id):
        try:
            user = request.user
            invitation = get_object_or_404(GameInvitation, id=invitation_id, to_user=user, status='pending')
            session = invitation.session
            if not session:
                return JsonResponse({'status': 'error', 'message': _("Cette invitation ne référence aucune session.")}, status=400)
            if session.player_right is not None:
                return JsonResponse({'status': 'error', 'message': _("Un second joueur est déjà positionné sur cette session.")}, status=400)
            if session.status != 'waiting':
                return JsonResponse({'status': 'error', 'message': _(f"La session n'est pas en attente (status={session.status}).")}, status=400)
            invitation.status = 'accepted'
            invitation.save()
            session.player_right = user
            session.save()
            schedule_game(session.id)
            GameInvitation.objects.filter(session=session, status='pending').exclude(id=invitation.id).update(status='expired')
            return JsonResponse({
                'status': 'success',
                'message': _("Invitation acceptée, session mise à jour."),
                'session': {
                    'id': str(session.id),
                    'player_left': session.player_left.username,
                    'player_right': session.player_right.username,
                    'status': session.status,
                }
            }, status=200)
        except Exception as e:
            logger.exception("Error in AcceptGameInvitationView: %s", e)
            return JsonResponse({'status': 'error', 'message': _("Internal server error")}, status=500)

@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class RejectGameInvitationView(View):
    """
    Permet au destinataire de rejeter une invitation.
    """
    def post(self, request, invitation_id):
        try:
            invitation = get_object_or_404(GameInvitation, id=invitation_id, to_user=request.user, status='pending')
            invitation.status = 'rejected'
            invitation.save()
            return JsonResponse({'status': 'success', 'message': _("Invitation refusée.")}, status=200)
        except Exception as e:
            logger.exception("Error in RejectGameInvitationView: %s", e)
            return JsonResponse({'status': 'error', 'message': _("Internal server error")}, status=500)

@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class CleanExpiredInvitationsView(View):
    """
    Marque les invitations expirées comme 'expired'.
    """
    def post(self, request):
        try:
            current_time = now()
            expired_count = GameInvitation.objects.filter(status='pending', expires_at__lt=current_time).update(status='expired')
            return JsonResponse({'status': 'success', 'message': _(f"{expired_count} invitations ont été expirées.")}, status=200)
        except Exception as e:
            logger.exception("Error in CleanExpiredInvitationsView: %s", e)
            return JsonResponse({'status': 'error', 'message': _("Internal server error")}, status=500)

@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class CheckGameInvitationStatusView(View):
    """
    Retourne le statut actuel d'une invitation.
    """
    def get(self, request, invitation_id):
        try:
            invitation = get_object_or_404(GameInvitation, id=invitation_id)
            if invitation.from_user != request.user and invitation.to_user != request.user:
                return JsonResponse({'status': 'error', 'message': _("Vous n'êtes pas autorisé à consulter cette invitation.")}, status=403)
            if invitation.is_expired() and invitation.status == 'pending':
                invitation.status = 'expired'
                invitation.save()
            return JsonResponse({
                'status': 'success',
                'invitation_status': invitation.status,
                'expired': invitation.is_expired(),
                'session_id': str(invitation.session.id) if invitation.session else None
            }, status=200)
        except Exception as e:
            logger.exception("Error in CheckGameInvitationStatusView: %s", e)
            return JsonResponse({'status': 'error', 'message': _("Internal server error")}, status=500)

@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
# class StartOnlineGameView(LoginRequiredMixin, View):
class JoinOnlineGameAsLeftView(View):
    
    def post(self, request, game_id):
        try:
            logger.debug("JoinOnlineGameAsLeftView")
            session = get_object_or_404(GameSession, id=game_id)
            if not session.is_online:
                return JsonResponse({'status': 'error', 'message': _("Cette session n'est pas une partie en ligne.")}, status=400)
            if request.user not in [session.player_left, session.player_right]:
                return JsonResponse({'status': 'error', 'message': _("Vous n'êtes pas autorisé à rejoindre cette partie.")}, status=403)
            if session.status in ['running', 'finished']:
                return JsonResponse({'status': 'error', 'message': _("La partie est déjà lancée ou terminée.")}, status=400)
            context = {
                'player_left_name': session.player_left.get_username(),
                'player_right_name': session.player_right.get_username(),
            }
            is_touch_param = request.POST.get('is_touch', 'false').strip().replace('/', '')
            is_touch = is_touch_param.lower() == 'true'
            if is_touch:
                rendered_html = render_to_string('game/live_game_tactile.html', context, request=request)
            else:
                rendered_html = render_to_string('game/live_game.html', context, request=request)
            return JsonResponse({
                'status': 'success',
                'html': rendered_html,
                'game_id': str(session.id),
                'message': _(f"Partie {game_id} rejointe (online).")
            }, status=200)
        except Exception as e:
            logger.exception("Error in JoinOnlineGameAsLeftView: %s", e)
            return JsonResponse({'status': 'error', 'message': _("Internal server error")}, status=500)

@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class JoinOnlineGameAsRightView(View):
    """
    Démarre la partie en ligne pour le joueur droit.
    """
    def post(self, request, game_id):
        try:
            logger.debug("JoinOnlineGameAsRightView")
            session = get_object_or_404(GameSession, id=game_id)
            if not session.is_online:
                return JsonResponse({'status': 'error', 'message': _("Cette session n'est pas une partie en ligne.")}, status=400)
            if request.user not in [session.player_left, session.player_right]:
                return JsonResponse({'status': 'error', 'message': _("Vous n'êtes pas autorisé à accéder à cette partie.")}, status=403)
            context = {
                'player_left_name': session.player_left.get_username(),
                'player_right_name': session.player_right.get_username(),
            }
            is_touch_param = request.POST.get('is_touch', 'false').strip().replace('/', '')
            is_touch = is_touch_param.lower() == 'true'
            if is_touch:
                rendered_html = render_to_string('game/live_game_tactile.html', context, request=request)
            else:
                rendered_html = render_to_string('game/live_game.html', context, request=request)
            return JsonResponse({
                'status': 'success',
                'html': rendered_html,
                'game_id': str(session.id),
                'message': _(f"Partie {game_id} lancée (online).")
            }, status=200)
        except Exception as e:
            logger.exception("Error in JoinOnlineGameAsRightView: %s", e)
            return JsonResponse({'status': 'error', 'message': _("Internal server error")}, status=500)

@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class StartOnlineGameView(View):
    """
    Démarre une partie en ligne.
    """
    def post(self, request, game_id):
        try:
            user_role = request.POST.get('userRole')
            if user_role not in ['left', 'right']:
                return JsonResponse({'status': 'error', 'message': _("Rôle utilisateur invalide. Attendu 'left' ou 'right'.")}, status=400)
            session = get_object_or_404(GameSession, id=game_id)
            logger.debug(f"StartOnlineGameView - Session: {session}")
            if not session.is_online:
                return JsonResponse({'status': 'error', 'message': _("La partie locale ne peut pas être lancée avec cette API.")}, status=400)
            if session.status == 'finished':
                return JsonResponse({'status': 'error', 'message': _(f"La partie {game_id} est déjà terminée.")}, status=400)
            if user_role == "right":
                session.ready_right = True
            elif user_role == "left":
                session.ready_left = True
            if session.ready_right and session.ready_left:
                session.status = 'running'
            session.save()
            logger.debug(f"StartOnlineGameView - Ready: {session.ready_left}-{session.ready_right}")
            return JsonResponse({'status': 'success', 'message': _(f"Partie {game_id} prête pour le joueur {user_role}.")}, status=200)
        except Exception as e:
            logger.exception("Error in StartOnlineGameView: %s", e)
            return JsonResponse({'status': 'error', 'message': _("Internal server error")}, status=500)
