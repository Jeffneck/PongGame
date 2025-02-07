import logging

from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.db import transaction
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ValidationError
from pong_project.decorators import login_required_json

from accounts.models import FriendRequest

# ---- Configuration ----
User = get_user_model()
logger = logging.getLogger(__name__)


class FriendValidationError(Exception):
    """
    Exception personnalisée pour les erreurs de validation d'ami.
    """
    pass


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class BaseFriendView(View):
    """
    Classe de base pour les vues liées aux amis, fournissant des méthodes utilitaires.
    """
    def validate_friend(self, user, friend_username):
        """
        Valide le nom d'utilisateur de l'ami et retourne l'instance utilisateur correspondante.
        """
        if not friend_username:
            raise FriendValidationError("Nom d'utilisateur de l'ami manquant")
        
        # Nettoyage de l'entrée (suppression des espaces superflus)
        friend_username = friend_username.strip()
        
        try:
            friend = User.objects.get(username=friend_username)
        except User.DoesNotExist:
            raise FriendValidationError("Ami introuvable")

        if friend == user:
            raise FriendValidationError("Vous ne pouvez pas vous envoyer une demande d'ami à vous-même.")

        return friend

    def create_json_response(self, status, message, status_code=200):
        """
        Méthode utilitaire pour créer des réponses JSON.
        """
        return JsonResponse({'status': status, 'message': message}, status=status_code)


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class AddFriendView(BaseFriendView):
    """
    Gère l'envoi de demandes d'ami.
    """
    def post(self, request):
        user = request.user
        # Nettoyage de l'entrée utilisateur
        friend_username = (request.POST.get('friend_username') or "").strip()
        try:
            friend = self.validate_friend(user, friend_username)
        except FriendValidationError as e:
            logger.error(f"Erreur lors de l'ajout d'un ami: {e}")
            return self.create_json_response('error', str(e), status_code=400)

        # Vérifie que l'utilisateur n'est pas déjà ami
        if friend in user.friends.all():
            logger.error(f"Erreur : {user.username} est déjà ami avec {friend.username}")
            return self.create_json_response('error', 'Vous êtes déjà ami avec cet utilisateur.', status_code=400)

        # Vérifie si une demande d'ami a déjà été envoyée ou reçue
        if FriendRequest.objects.filter(from_user=user, to_user=friend).exists():
            logger.error(f"Erreur : Demande d'ami déjà envoyée de {user.username} à {friend.username}")
            return self.create_json_response('error', "Demande d'ami déjà envoyée.", status_code=400)

        if FriendRequest.objects.filter(from_user=friend, to_user=user).exists():
            logger.error(f"Erreur : Demande d'ami déjà reçue de {friend.username} pour {user.username}")
            return self.create_json_response('error', "Cet utilisateur vous a déjà envoyé une demande d'ami.", status_code=400)

        # Création de la demande d'ami
        FriendRequest.objects.create(from_user=user, to_user=friend)
        logger.info(f"Demande d'ami envoyée de {user.username} à {friend.username}.")
        return self.create_json_response('success', "Demande d'ami envoyée.", status_code=200)


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class HandleFriendRequestView(View):
    """
    Gère l'acceptation ou le refus des demandes d'ami.
    """
    @transaction.atomic
    def post(self, request):
        user = request.user
        try:
            request_id = request.POST.get('request_id')
            action = request.POST.get('action')
            
            logger.debug(f"Traitement de la demande d'ami ID: {request_id} pour {user.username}")

            # Récupère la demande d'ami
            friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=user)

            if action == 'accept':
                # Ajoute les deux utilisateurs comme amis
                user.friends.add(friend_request.from_user)
                friend_request.from_user.friends.add(user)

                # Supprime la demande d'ami
                friend_request.delete()
                logger.info(f"Demande d'ami acceptée entre {user.username} et {friend_request.from_user.username}.")
                return JsonResponse({'status': 'success', 'message': "Demande d'ami acceptée"}, status=200)

            elif action == 'decline':
                # Supprime la demande d'ami
                friend_request.delete()
                logger.info(f"Demande d'ami refusée entre {user.username} et {friend_request.from_user.username}.")
                return JsonResponse({'status': 'success', 'message': "Demande d'ami refusée"}, status=200)

            else:
                logger.warning("Action non valide lors du traitement de la demande d'ami")
                return JsonResponse({'status': 'error', 'message': "Action non valide"}, status=400)

        except Exception as e:
            logger.error(f"Erreur lors du traitement de la demande d'ami: {e}")
            return JsonResponse({'status': 'error', 'message': "Erreur lors de la gestion de la demande d'ami"}, status=500)


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class RemoveFriendView(BaseFriendView):
    """
    Gère la suppression d'un ami.
    """
    def post(self, request):
        user = request.user
        friend_username = (request.POST.get('friend_username') or "").strip()
        try:
            friend = self.validate_friend(user, friend_username)
        except FriendValidationError as e:
            logger.error(f"Erreur lors de la suppression d'un ami: {e}")
            return self.create_json_response('error', str(e), status_code=400)

        if friend not in user.friends.all():
            logger.error(f"Erreur : {friend.username} n'est pas dans la liste d'amis de {user.username}")
            return self.create_json_response('error', "Cet utilisateur n'est pas dans votre liste d'amis.", status_code=400)

        # Suppression réciproque de l'ami
        user.friends.remove(friend)
        friend.friends.remove(user)

        logger.info(f"Suppression de l'amitié entre {user.username} et {friend.username}.")
        return self.create_json_response('success', "Ami supprimé avec succès.", status_code=200)
