# ---- Imports standard ----
import logging

# ---- Imports tiers ----
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.template.loader import render_to_string


# ---- Imports locaux ----
from accounts.models import FriendRequest
from game.models import GameInvitation

# ---- Configuration ----
logger = logging.getLogger(__name__)
User = get_user_model()

def get_burger_menu_context(user):
    """
    Retourne le contexte nécessaire pour le template du burger menu.
    """
    default_avatar = '/media/avatars/default_avatar.png'
    return {
        'user': user,
        'friends': user.friends.all(),
        'friend_requests': FriendRequest.objects.filter(to_user=user),
        'game_invitations': GameInvitation.objects.filter(to_user=user, status='pending'),
        'avatar_url': user.avatar.url if user.avatar else default_avatar,
    }

class BurgerMenuView(View):
    """
    Handle retrieval of user data for the burger menu.
    """

    @method_decorator(login_required)
    def get(self, request):
        """
        Render the burger menu with user data, friends list, and friend requests.
        """
        try:
            context = get_burger_menu_context(request.user)
            burger_menu_html = render_to_string('accounts/burger_menu.html', context)
            return JsonResponse({'status': 'success', 'html': burger_menu_html})
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données du menu burger: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@method_decorator([csrf_protect, login_required], name='dispatch')
class UpdateStatusView(View):
    """
    Handle updating the user's online/offline status.
    """

    def post(self, request):
        """
        Update the user's online/offline status.
        """
        user = request.user
        status = request.POST.get('status')

        logger.info(f"--Requête de mise à jour du statut pour {user.username}: {status}")

        if status not in ['online', 'offline']:
            return JsonResponse({'status': 'error', 'message': 'Statut non valide'}, status=400)

        # Update the user's status
        user.is_online = (status == 'online')
        user.save()

        logger.info(f"Statut mis à jour pour {user.username}: {user.is_online}")
        return JsonResponse({'status': 'success', 'message': 'Statut mis à jour avec succès', 'is_online': user.is_online})
