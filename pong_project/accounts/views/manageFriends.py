# ---- Imports standard ----
import logging

# ---- Imports tiers ----
from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError

# ---- Imports locaux ----
from accounts.models import FriendRequest

# ---- Configuration ----
User = get_user_model()
logger = logging.getLogger(__name__)

class FriendValidationError(Exception):
    """
    Custom exception for friend validation errors.
    """
    pass

class BaseFriendView(View):
    """
    Base class for friend-related views, providing utility methods.
    """
    def validate_friend(self, user, friend_username):
        """
        Validates the friend username and returns the friend user instance.
        """
        if not friend_username:
            raise FriendValidationError('Nom d\'utilisateur de l\'ami manquant')

        friend = get_object_or_404(User, username=friend_username)

        if friend == user:
            raise FriendValidationError('Vous ne pouvez pas vous envoyer une demande d\'ami à vous-même.')

        return friend

    def create_json_response(self, status, message, status_code=200):
        """
        Utility method to create JSON responses.
        """
        return JsonResponse({'status': status, 'message': message}, status=status_code)

@method_decorator(login_required, name='dispatch')
class AddFriendView(BaseFriendView):
    """
    Handles sending friend requests.
    """
    def post(self, request):
        user = request.user
        friend_username = request.POST.get('friend_username')


        try:
            friend = self.validate_friend(user, friend_username)
        except FriendValidationError as e:
            logger.error(f"Error adding friend: {e}")
            return self.create_json_response('error', str(e), 400)

        if friend in user.friends.all():
            logger.error(f"Error adding friend: {user.username} is already friends with {friend.username}")
            return self.create_json_response('error', 'Vous êtes déjà ami avec cet utilisateur.', 400)

        if FriendRequest.objects.filter(from_user=user, to_user=friend).exists():
            logger.error(f"Error adding friend: Friend request already sent from {user.username} to {friend.username}")
            return self.create_json_response('error', 'Demande d\'ami déjà envoyée.', 400)

        if FriendRequest.objects.filter(from_user=friend, to_user=user).exists():
            logger.error(f"Error adding friend: Friend request already received from {friend.username} to {user.username}")
            return self.create_json_response('error', 'Cet utilisateur vous a déjà envoyé une demande d\'ami.', 400)

        FriendRequest.objects.create(from_user=user, to_user=friend)
        logger.info(f"Demande d'ami envoyée de {user.username} à {friend.username}.")
        return self.create_json_response('success', 'Demande d\'ami envoyée.')

@method_decorator(login_required, name='dispatch')
class HandleFriendRequestView(View):
    """
    Handles acceptance or rejection of friend requests.
    """
    @transaction.atomic
    def post(self, request):
        user = request.user
        try:
            request_id = request.POST.get('request_id')
            action = request.POST.get('action')

            logger.debug(f"Handling friend request ID: {request_id} for user {user.username}")

            # Retrieve the friend request
            friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=user)

            if action == 'accept':
                # Add both users as friends
                user.friends.add(friend_request.from_user)
                friend_request.from_user.friends.add(user)

                # Delete the friend request
                friend_request.delete()
                logger.info(f"Demande d'ami acceptée entre {user.username} et {friend_request.from_user.username}.")
                return JsonResponse({'status': 'success', 'message': 'Demande d\'ami acceptée'})

            elif action == 'decline':
                # Delete the friend request
                friend_request.delete()
                logger.info(f"Demande d'ami refusée entre {user.username} et {friend_request.from_user.username}.")
                return JsonResponse({'status': 'success', 'message': 'Demande d\'ami refusée'})

            else:
                return JsonResponse({'status': 'error', 'message': 'Action non valide'}, status=400)

        except Exception as e:
            logger.error(f"Error handling friend request: {e}")
            return JsonResponse({'status': 'error', 'message': 'Erreur lors de la gestion de la demande d\'ami'}, status=500)

@method_decorator(login_required, name='dispatch')
class RemoveFriendView(BaseFriendView):
    """
    Handles the removal of a friend.
    """
    def post(self, request):
        user = request.user
        friend_username = request.POST.get('friend_username')

        try:
            friend = self.validate_friend(user, friend_username)
        except FriendValidationError as e:
            return self.create_json_response('error', str(e), 400)

        if friend not in user.friends.all():
            return self.create_json_response('error', 'Cet utilisateur n\'est pas dans votre liste d\'amis.', 400)

        # Remove the friend from both users' friend lists
        user.friends.remove(friend)
        friend.friends.remove(user)

        logger.info(f"Friendship removed between {user.username} and {friend.username}.")
        return self.create_json_response('success', 'Ami supprimé avec succès.')
