# ---- Imports standard ----
import logging

# ---- Imports tiers ----
from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Max
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.db.models import Q
from game.models import GameResult

# ---- Imports locaux ----

# ---- Configuration ----
logger = logging.getLogger(__name__)
User = get_user_model()



@method_decorator([csrf_protect, login_required], name='dispatch')
class FriendProfileView(View):
    """
    Display the profile of a friend, including statistics, metadata, and match history.
    """

    def get(self, request, friend_username):
        logger.debug("Entering FriendProfileView.get()")
        logger.debug(f"Friend_username = {friend_username}")
        try:
            # Récupérer l'ami par son nom d'utilisateur
            friend = get_object_or_404(User, username=friend_username)
            logger.info(f"User found: {friend.username}")

            # Calcul des statistiques supplémentaires pour l'ami
            matches = GameResult.objects.filter(Q(player1=friend) | Q(player2=friend))
            match_count = matches.count()
            victories = matches.filter(winner=friend).count()
            defeats = match_count - victories
            best_score = max(
                matches.filter(player1=friend).aggregate(Max('score_player1'))['score_player1__max'] or 0,
                matches.filter(player2=friend).aggregate(Max('score_player2'))['score_player2__max'] or 0,
            )
            friends_count = friend.friends.count()

            logger.info(
                f"Statistics calculated: match_count={match_count}, victories={victories}, "
                f"defeats={defeats}, best_score={best_score}, friends_count={friends_count}"
            )

            # Calcul de l'historique des matchs
            match_histories = []
            for match in matches.order_by('-date'):
                opponent = match.player1 if match.player2 == friend else match.player2
                match_histories.append({
                    'opponent': opponent.username,
                    'result': 'win' if match.winner == friend else 'loss' if not match.is_draw else 'draw',
                    'score': f"{match.score_player1} - {match.score_player2}",
                    'played_at': match.date,
                })

            # Préparer le contexte pour rendre le template
            default_avatar = '/media/avatars/default_avatar.png'
            context = {
                'friend': friend,
                'avatar_url': friend.avatar.url if friend.avatar else default_avatar,
                'match_count': match_count,
                'victories': victories,
                'defeats': defeats,
                'best_score': best_score,
                'friends_count': friends_count,
                'match_histories': match_histories,  # Ajouter l'historique des matchs
            }

            # Rendre le template en HTML
            rendered_html = render_to_string('accounts/friend_profile.html', context)

            return JsonResponse({
                'status': 'success',
                'html': rendered_html,
            }, status=200)

        except Exception as e:
            logger.error(f"Error loading friend profile: {e}")
            return JsonResponse({'status': 'error', 'message': 'Erreur lors du chargement du profil de l\'ami.'}, status=500)

