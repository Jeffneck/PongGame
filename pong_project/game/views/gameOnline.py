# game/views/gameOnline.py

import logging
from django.views import View
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.timezone import now
from pong_project.decorators import login_required_json
from django.utils.translation import gettext_lazy as _


from game.models import GameSession
from game.forms import GameParametersForm
from game.manager import schedule_game


# invitation
from django.shortcuts import get_object_or_404
from django.db.models import Q

from accounts.models import CustomUser
from game.models import GameInvitation, GameSession

logger = logging.getLogger(__name__)

# le flux complet ressemble à :
#
# (Joueur 1) Création session (status=waiting) → On l’affiche (loading.html).
# (Joueur 1) Envoie invitation → L’autre reçoit.
# (Joueur 2) Accepte (session.status = ready)
# (Joueur 1) Vérifie en poll (CheckGameInvitationStatusView) → voit accepted
# (Joueur 1) Appuie sur « Démarrer » (loading.html) → StartOnlineGameView (session.status = running)
# Les 2 → redirection vers live_online_game.html?game_id=xxx, connexion WebSocket, etc.
@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class CreateGameOnlineView(View):
    """
    Crée une GameSession en ligne (player_left = request.user), 
    enregistre les paramètres via GameParameters, puis renvoie 
    un HTML de salle d’attente ou un simple JSON.
    """
    def post(self, request):
        form = GameParametersForm(request.POST)
        logger.debug("Rentre dans CREATE GAME LIVE (en ligne)")
        if not form.is_valid():
            return JsonResponse({
                'status': 'error',
                'message': _("Paramètres invalides."),
                'errors': form.errors
            }, status=400)

        session = GameSession.objects.create(
            status='waiting',
            is_online=True,
            player_left=request.user  # Le créateur de la partie
        )

        parameters = form.save(commit=False)
        parameters.game_session = session
        parameters.save()

        logger.debug(f"[CreateGameLiveView] Session {session.id} créée, en attente du joueur adverse.")
        friends = request.user.friends.all()
        if not friends.exists():
            return JsonResponse({
                'status': 'error',
                'message': _("Vous n'avez pas encore ajouté d'amis. Ajoutez des amis pour les inviter à jouer.")
            })

        rendered_html = render_to_string('game/online_game/invite_game.html', {
            'game_id': session.id,
            'friends': friends,
        }, request=request)

        return JsonResponse({
            'status': 'success',
            'message': _("Partie en ligne créée avec succès."),
            'game_id': str(session.id),
            'html': rendered_html
        })


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class SendGameSessionInvitationView(View):
    """
    Le joueur (request.user) envoie une invitation à friend_username
    pour la session (session_id) déjà créée en ligne.
    """
    def post(self, request):
        session_id = request.POST.get('session_id')
        friend_username = request.POST.get('friend_username')

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
            session=session,     # <= on lie la session existante
            status='pending'
        )

        rendered_html = render_to_string('game/online_game/loading.html')

        return JsonResponse({
            'status': 'success',
            'html': rendered_html,
            'message': _("Invitation envoyée."),
            'invitation_id': invitation.id
        })


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class AcceptGameInvitationView(View):
    """
    Le second joueur accepte l'invitation.
    Au lieu de créer la session ici, on récupère 
    celle créée en amont par le 1er joueur.
    La partie est lancée en coroutine dans cette vue.
    """
    def post(self, request, invitation_id):
        user = request.user
        invitation = get_object_or_404(
            GameInvitation, 
            id=invitation_id, 
            to_user=user, 
            status='pending'
        )

        session = invitation.session
        if not session:
            return JsonResponse({
                'status': 'error',
                'message': _("Cette invitation ne référence aucune session.")
            }, status=400)

        if session.player_right is not None:
            return JsonResponse({
                'status': 'error',
                'message': _("Un second joueur est déjà positionné sur cette session.")
            }, status=400)

        if session.status not in ['waiting']:
            return JsonResponse({
                'status': 'error',
                'message': _("La session n'est pas en attente (status=%(status)s).") % {'status': session.status}
            }, status=400)

        invitation.status = 'accepted'
        invitation.save()

        session.player_right = user
        session.save()

        schedule_game(session.id)

        GameInvitation.objects.filter(
            session=session,
            status='pending'
        ).exclude(id=invitation.id).update(status='expired')

        return JsonResponse({
            'status': 'success',
            'message': _("Invitation acceptée, session mise à jour."),
            'session': {
                'id': str(session.id),
                'player_left': session.player_left.username,
                'player_right': session.player_right.username,
                'status': session.status,
            }
        })


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class RejectGameInvitationView(View):
    """
    Permet au destinataire d'une invitation de la rejeter.
    """
    def post(self, request, invitation_id):
        invitation = get_object_or_404(
            GameInvitation,
            id=invitation_id,
            to_user=request.user,  # seul le destinataire peut rejeter
            status='pending'
        )

        invitation.status = 'rejected'
        invitation.save()

        return JsonResponse({
            'status': 'success',
            'message': _("Invitation refusée.")
        })


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class CleanExpiredInvitationsView(View):
    """
    Marque toutes les invitations 'pending' dont la date d'expiration est dépassée
    comme 'expired'.
    """
    def post(self, request):
        now_ = now()
        expired_count = GameInvitation.objects.filter(
            status='pending',
            expires_at__lt=now_
        ).update(status='expired')

        return JsonResponse({
            'status': 'success',
            'message': _('%(count)d invitations ont été expirées.') % {'count': expired_count}
        })


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class CheckGameInvitationStatusView(View):
    """
    Retourne le statut actuel de l'invitation (pending, accepted, rejected, expired).
    Ainsi, le front peut décider de rediriger le joueur 1 
    soit vers le Start, soit vers un message d'erreur, etc.
    """
    def get(self, request, invitation_id):
        invitation = get_object_or_404(GameInvitation, id=invitation_id)
        
        if invitation.from_user != request.user and invitation.to_user != request.user:
            return JsonResponse({
                'status': 'error',
                'message': _("Vous n'êtes pas autorisé à consulter cette invitation.")
            }, status=403)

        if invitation.is_expired() and invitation.status == 'pending':
            invitation.status = 'expired'
            invitation.save()

        return JsonResponse({
            'status': 'success',
            'invitation_status': invitation.status,
            'expired': invitation.is_expired(),
            'session_id': str(invitation.session.id) if invitation.session else None
        })


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class JoinOnlineGameAsLeftView(View):
    def post(self, request, game_id):
        logger.debug("JoinOnlineGameAsLeftView")
        try:
            session = GameSession.objects.get(id=game_id)
        except GameSession.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': _("La session de jeu spécifiée n'existe pas.")
            }, status=404)

        if not session.is_online:
            return JsonResponse({
                'status': 'error',
                'message': _("Cette session n'est pas une partie en ligne.")
            }, status=400)

        if request.user not in [session.player_left, session.player_right]:
            return JsonResponse({
                'status': 'error',
                'message': _("Vous n'êtes pas autorisé à rejoindre cette partie.")
            }, status=403)

        if session.status in ['running', 'finished']:
            return JsonResponse({
                'status': 'error',
                'message': _("La partie est déjà lancée ou terminée.")
            }, status=400)

        context = {
            'player_left_name': session.player_left.get_username(),
            'player_right_name': session.player_right.get_username(),
        }

        # Récupérer le paramètre is_touch depuis le POST et le nettoyer
        is_touch_param = request.POST.get('is_touch', 'false').strip().replace('/', '')
        is_touch = is_touch_param.lower() == 'true'

        if is_touch:
            print("is_touch == TRUE")
            rendered_html = render_to_string('game/live_game_tactile.html', context)
        else:
            print("is_touch == FALSE")
            rendered_html = render_to_string('game/live_game.html', context)
     
        return JsonResponse({
            'status': 'success',
            'html': rendered_html,
            'game_id': str(session.id),
            'message': _("Partie %(game_id)s rejointe (online).") % {'game_id': game_id}
        })


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class JoinOnlineGameAsRightView(View):
    """
    Démarre la partie en ligne.
    """
    def post(self, request, game_id):
        logger.debug("JoinOnlineGameAsRightView")
        print("WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWw")
        try:
            session = GameSession.objects.get(id=game_id)
        except GameSession.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': _("La session de jeu spécifiée n'existe pas.")
            }, status=404)

        if not session.is_online:
            return JsonResponse({
                'status': 'error',
                'message': _("Cette session n'est pas une partie en ligne.")
            }, status=400)

        if request.user not in [session.player_left, session.player_right]:
            return JsonResponse({
                'status': 'error',
                'message': _("Vous n'êtes pas autorisé à accéder à cette partie.")
            }, status=403)
        
        context = {
            'player_left_name': session.player_left.get_username(),
            'player_right_name': session.player_right.get_username(),
        }
        
        # Récupérer le paramètre is_touch depuis le POST et le nettoyer
        is_touch_param = request.POST.get('is_touch', 'false').strip().replace('/', '')
        is_touch = is_touch_param.lower() == 'true'

        if is_touch:
            print("is_touch == TRUE")
            rendered_html = render_to_string('game/live_game_tactile.html', context)
        else:
            print("is_touch == FALSE")
            rendered_html = render_to_string('game/live_game.html', context)

        return JsonResponse({
            'status': 'success',
            'html' : rendered_html,
            'game_id': str(session.id),
            'message': _("Partie %(game_id)s lancée (online).") % {'game_id': game_id}
        })
    

@method_decorator(csrf_protect, name='dispatch')
class StartOnlineGameView(View):
    """
    Démarre la partie online en exécutant la logique du jeu.
    """
    def post(self, request, game_id):
        user_role = request.POST.get('userRole')
        if user_role not in ['left', 'right']:
            return JsonResponse({
                'status': 'error',
                'message': _("Rôle utilisateur invalide. Attendu 'left' ou 'right'.")
            }, status=400)
        
        try:
            session = GameSession.objects.get(id=game_id)
        except GameSession.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': _("La session de jeu spécifiée n'existe pas.")
            }, status=404)

        print(f"[DEBUG] StartOnlineGameView gameSession: {session}")

        if not session.is_online:
            return JsonResponse({
                'status': 'error',
                'message': _("La partie locale ne peut pas être lancée avec cette API. Cette API sert à lancer une partie online.")
            }, status=400)

        if session.status == 'finished':
            return JsonResponse({
                'status': 'error',
                'message': _("La partie %(game_id)s est déjà terminée et ne peut pas être relancée.") % {'game_id': game_id}
            }, status=400)

        if user_role == "right":
            session.ready_right = True
        elif user_role == "left":
            session.ready_left = True
        if (session.ready_right and session.ready_left):
            session.status = 'running'

        session.save()
        print(f"[DEBUG] StartOnlineGameView ready :  {session.ready_left}-{session.ready_right}")

        return JsonResponse({
            'status': 'success',
            'message': _("Partie %(game_id)s prête pour le joueur %(user_role)s.") % {'game_id': game_id, 'user_role': user_role}
        })
