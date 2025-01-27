# ---- Imports standard ----
import logging

# ---- Imports tiers ----
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.template.loader import render_to_string
from django.db.models import Max
from django.contrib.auth import get_user_model
from django.db.models import Q
from game.models import GameResult

# ---- Configuration ----
logger = logging.getLogger(__name__)
User = get_user_model()


from django.shortcuts import render

@method_decorator(csrf_protect, name='dispatch')
class ProfileView(View):
    def get(self, request):
        logger.debug("Entering ProfileView.get()")
        try:
            user = request.user
            logger.info(f"User found: {user.username}")

            # Calcul des statistiques utilisateur
            matches = GameResult.objects.filter(Q(player1=user) | Q(player2=user))
            match_count = matches.count()
            victories = matches.filter(winner=user).count()
            defeats = match_count - victories
            best_score = max(
                matches.filter(player1=user).aggregate(Max('score_player1'))['score_player1__max'] or 0,
                matches.filter(player2=user).aggregate(Max('score_player2'))['score_player2__max'] or 0,
            )
            friends_count = user.friends.count()

            match_histories = []
            for match in matches:
                opponent = match.get_opponent(user)
                match_histories.append({
                    'opponent': opponent,
                    'result': 'win' if match.winner == user else 'loss',
                    'score_user': match.score_player1 if match.player1 == user else match.score_player2,
                    'score_opponent': match.score_player2 if match.player1 == user else match.score_player1,
                    'played_at': match.date,
                })
            logger.info(
                f"Statistics calculated: match_count={match_count}, victories={victories}, "
                f"defeats={defeats}, best_score={best_score}, friends_count={friends_count}"
            )

            context = {
            'user': user,
            'match_count': match_count,
            'victories': victories,
            'defeats': defeats,
            'best_score': best_score,
            'friends_count': friends_count,
            'match_histories': match_histories,
            }

            rendered_html = render_to_string('accounts/profile.html', context)

            return JsonResponse({
                'status': 'success',
                'html': rendered_html,
            }, status=200)

        except Exception as e:
            logger.error(f"Error loading user profile: {e}")
            return JsonResponse({'status': 'error', 'message': 'An error occurred while loading the profile.'}, status=500)
