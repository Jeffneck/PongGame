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

# (Joueur 1) Création session (status=waiting) → On l’affiche (loading.html).
# (Joueur 1) Envoie invitation → L’autre reçoit.
# (Joueur 2) Accepte (session.status = ready)
# (Joueur 1) Vérifie en poll (CheckGameInvitationStatusView) → voit accepted
# (Joueur 1) Appuie sur « Démarrer » (loading.html) → StartOnlineGameView (session.status = running)
# Les 2 → redirection vers live_online_game.html?game_id=xxx, connexion WebSocket, etc.

@method_decorator(csrf_protect, name='dispatch')
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
                'message': "Paramètres invalides.",
                'errors': form.errors
            }, status=400)

        # 1) Création de la GameSession online
        session = GameSession.objects.create(
            status='waiting',
            is_online=True,
            player_left=request.user  # Le créateur de la partie
        )

        # 2) Création des paramètres
        parameters = form.save(commit=False)
        parameters.game_session = session
        parameters.save()

        logger.debug(f"[CreateGameLiveView] Session {session.id} créée, en attente du joueur adverse.")
        friends = request.user.friends.all()
        if not friends.exists():
            return JsonResponse({
                'status': 'error',
                'message': "Vous n'avez pas encore ajouté d'amis. Ajoutez des amis pour les inviter à jouer."
            })
        

        # 3) On peut injecter le HTML de la page d'invitation
        rendered_html = render_to_string('game/online_game/invite_game.html', {
            'game_id': session.id,
            'friends': friends,
        }, request=request)

        return JsonResponse({
            'status': 'success',
            'message': "Partie en ligne créée avec succès.",
            'game_id': str(session.id),
            'html': rendered_html
        })


@method_decorator(csrf_protect, name='dispatch')
class SendGameSessionInvitationView(LoginRequiredMixin, View):
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
                'message': 'Données manquantes (session_id ou friend_username).'
            }, status=400)

        # Récupérer la session
        session = get_object_or_404(GameSession, id=session_id, is_online=True)
        # Vérifier que request.user est bien le player_left
        if session.player_left != request.user:
            return JsonResponse({
                'status': 'error',
                'message': "Vous n'êtes pas autorisé à inviter pour cette session."
            }, status=403)

        # Récupérer l'ami
        try:
            friend = CustomUser.objects.get(username=friend_username)
        except CustomUser.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': "Ami introuvable."
            }, status=404)

        if friend == request.user:
            return JsonResponse({
                'status': 'error',
                'message': "Vous ne pouvez pas vous inviter vous-même."
            }, status=400)

        # Vérifier qu'on n'a pas déjà une invitation en attente pour cette session
        existing_invitation = GameInvitation.objects.filter(
            from_user=request.user,
            to_user=friend,
            session=session,
            status='pending'
        ).first()

        if existing_invitation:
            return JsonResponse({
                'status': 'error',
                'message': "Une invitation est déjà en attente pour cette session."
            }, status=400)

        # Créer l'invitation
        invitation = GameInvitation.objects.create(
            from_user=request.user,
            to_user=friend,
            session=session,     # <= on lie la session existante
            status='pending'
        )

        # 3) On peut injecter le HTML de la page d'invitation
        rendered_html = render_to_string('game/online_game/loading.html')

        return JsonResponse({
            'status': 'success',
            'html': rendered_html,
            'message': 'Invitation envoyée.',
            'invitation_id': invitation.id
        })


#cette vue pourrait génerer l'url de la game session pour que l'utilisateur qui accepte l'invitation soit redirigé vers la page de jeu
@method_decorator([csrf_protect, login_required], name='dispatch')
class AcceptGameInvitationView(View):
    """
    Le second joueur accepte l'invitation.
    Au lieu de créer la session ici, on récupère 
    celle créée en amont par le 1er joueur.
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
                'message': "Cette invitation ne référence aucune session."
            }, status=400)

        # Vérifier que la session n'est pas déjà prise
        if session.player_right is not None:
            return JsonResponse({
                'status': 'error',
                'message': "Un second joueur est déjà positionné sur cette session."
            }, status=400)

        # Vérifier qu'elle est encore 'waiting'
        if session.status not in ['waiting']:
            return JsonResponse({
                'status': 'error',
                'message': f"La session n'est pas en attente (status={session.status})."
            }, status=400)

        # Acceptation
        invitation.status = 'accepted'
        invitation.save()

        # le joueur invite devient le player_right sur la session
        session.player_right = user
        session.save()

        #on lance le jeu au moment de l' acceptation de l' invitation
        schedule_game(session.id)

        # Expirer les autres invitations "pending" pour cette session, si besoin
        GameInvitation.objects.filter(
            session=session,
            status='pending'
        ).exclude(id=invitation.id).update(status='expired')

        return JsonResponse({
            'status': 'success',
            'message': 'Invitation acceptée, session mise à jour.',
            'session': {
                'id': str(session.id),
                'player_left': session.player_left.username,
                'player_right': session.player_right.username,
                'status': session.status,
            }
        })


@method_decorator([csrf_protect, login_required], name='dispatch')
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

        if invitation.session and invitation.session.status == 'waiting':
            # Soit on supprime la session
            invitation.session.delete()
            # ou on la marque 'cancelled'
            # invitation.session.status = 'cancelled'
            # invitation.session.save()

        invitation.status = 'rejected'
        invitation.save()

        return JsonResponse({
            'status': 'success',
            'message': "Invitation refusée."
        })


@method_decorator(login_required, name='dispatch')
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
            'message': f"{expired_count} invitations ont été expirées."
        })


@method_decorator(login_required, name='dispatch')
class CheckGameInvitationStatusView(View):
    """
    Retourne le statut actuel de l'invitation (pending, accepted, rejected, expired).
    Ainsi, le front peut décider de rediriger le joueur 1 
    soit vers le Start, soit vers un message d'erreur, etc.
    """
    def get(self, request, invitation_id):
        invitation = get_object_or_404(GameInvitation, id=invitation_id)
        
        # On vérifie que le user en question est impliqué 
        # (soit l'expéditeur, soit le destinataire), sinon 403
        if invitation.from_user != request.user and invitation.to_user != request.user:
            return JsonResponse({
                'status': 'error',
                'message': "Vous n'êtes pas autorisé à consulter cette invitation."
            }, status=403)

        # Pour la propreté, on peut aussi marquer l'invitation expirée si la date est dépassée
        if invitation.is_expired() and invitation.status == 'pending':
            invitation.status = 'expired'
            invitation.save()

        return JsonResponse({
            'status': 'success',
            'invitation_status': invitation.status,
            'expired': invitation.is_expired(),
            'session_id': str(invitation.session.id) if invitation.session else None
        })

# lancee par le front du player Left au moment de l'acceptation de l'invitation par le player right
# IMPROVE pourrait etre une requete get ?
@method_decorator(csrf_protect, name='dispatch')
# class StartOnlineGameView(LoginRequiredMixin, View):
class JoinOnlineGameAsLeftView(LoginRequiredMixin, View):
    def get(self, request, game_id):
        try:
            session = GameSession.objects.get(id=game_id)
        except GameSession.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': "La session de jeu spécifiée n'existe pas."
            }, status=404)

        # Vérifier que c'est une partie en ligne
        if not session.is_online:
            return JsonResponse({
                'status': 'error',
                'message': "Cette session n'est pas une partie en ligne."
            }, status=400)

        # Vérifier que l'utilisateur est player_left OU player_right
        if request.user not in [session.player_left, session.player_right]:
            return JsonResponse({
                'status': 'error',
                'message': "Vous n'êtes pas autorisé à rejoindre cette partie."
            }, status=403)

        # Vérifier que la partie n'est pas déjà lancée/finie
        if session.status in ['running', 'finished']:
            return JsonResponse({
                'status': 'error',
                'message': "La partie est déjà lancée ou terminée."
            }, status=400)

        # Injecter le HTML de la page de jeu
        rendered_html = render_to_string('game/online_game/live_online_game_left.html', {
            'game_id': session.id,
        }, request=request)

        return JsonResponse({
            'status': 'success',
            'html': rendered_html,
            'game_id': str(session.id),
            'message': f"Partie {game_id} rejointe (online)."
        })

# lancee par le front du player RIGHT au moment de l'acceptation de l'invitation par le player right
@method_decorator(csrf_protect, name='dispatch')
class JoinOnlineGameAsRightView(LoginRequiredMixin, View):
    """
    Démarre la partie en ligne.
    """
    def get(self, request, game_id):
        try:
            session = GameSession.objects.get(id=game_id)
        except GameSession.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': "La session de jeu spécifiée n'existe pas."
            }, status=404)

        if not session.is_online:
            return JsonResponse({
                'status': 'error',
                'message': "Cette session n'est pas une partie en ligne."
            }, status=400)

        if request.user not in [session.player_left, session.player_right]:
            return JsonResponse({
                'status': 'error',
                'message': "Vous n'êtes pas autorisé à accéder à cette partie."
            }, status=403)
        
        # On peut injecter le HTML de la page de jeu
        rendered_html = render_to_string('game/online_game/live_online_game_right.html')

        return JsonResponse({
            'status': 'success',
            'html' : rendered_html,
            'game_id': str(session.id),
            'message': f"Partie {game_id} lancée (online)."
        })
    
   


# lancee par l'appui sur le bouton PLAY, marque le joueur comme pr^et dans la game session
#la gameLoop attend pendant 20 secondes que les 2 joueurs aiet indique qu' ils sont prets
@method_decorator(csrf_protect, name='dispatch')
class StartOnlineGameView(View):
    """
    Démarre la partie online en exécutant la logique du jeu.
    """
    def post(self, request, game_id):
        # Récupérer le rôle de l'utilisateur depuis les données POST
        user_role = request.POST.get('userRole')
        if user_role not in ['left', 'right']:
            return JsonResponse({
                'status': 'error',
                'message': "Rôle utilisateur invalide. Attendu 'left' ou 'right'."
            }, status=400)
        
        try:
            # Récupérer la session de jeu par son ID
            session = GameSession.objects.get(id=game_id)
        except GameSession.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': "La session de jeu spécifiée n'existe pas."
            }, status=404)

        # Debug : Afficher la session récupérée
        print(f"[DEBUG] StartOnlineGameView gameSession: {session}")

        # Vérifier que la session correspond bien à une partie online
        if not session.is_online:
            return JsonResponse({
                'status': 'error',
                'message': "La partie locale ne peut pas être lancée avec cette API. Cette API sert à lancer une partie online."
            }, status=400)

        # Vérifier que la partie n'est pas déjà terminée
        if session.status == 'finished':
            return JsonResponse({
                'status': 'error',
                'message': f"La partie {game_id} est déjà terminée et ne peut pas être relancée."
            }, status=400)

        # Mise à jour du statut en fonction du rôle utilisateur
        if user_role == "right":
            session.ready_player_right = True
        elif user_role == "left":
            session.ready_player_left = True

        session.save()

        return JsonResponse({
            'status': 'success',
            'message': f"Partie {game_id} prête pour le joueur {user_role}."
        })

