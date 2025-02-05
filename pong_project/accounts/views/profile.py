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
from django.contrib.auth.decorators import login_required
from pong_project.decorators import login_required_json

from game.models import GameResult  # Import du modèle mis à jour

# ---- Configuration ----
logger = logging.getLogger(__name__)
User = get_user_model()

@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class ProfileView(View):
    def get(self, request):
        logger.debug("Entering ProfileView.get()")
        try:
            user = request.user
            logger.info(f"User found: {user.username}")

            # ✅ Utilisation du Manager pour récupérer l'historique des matchs
            matches = GameResult.objects.get_user_match_history(user)
            match_count = matches.count()

            # ✅ Corrigé : Comparaison avec `user` et non `user.username`
            victories = matches.filter(winner=user).count()
            defeats = matches.filter(looser=user).count()

            # ✅ Corrigé : Comparaison avec `user` et non `user.username`
            best_score = max(
                matches.filter(game__player_left=user).aggregate(Max('score_left'))['score_left__max'] or 0,
                matches.filter(game__player_right=user).aggregate(Max('score_right'))['score_right__max'] or 0,
            )

            friends_count = user.friends.count()

            match_histories = []
            for match in matches:
                opponent = match.game.player_right if match.game.player_left == user else match.game.player_left
                match_histories.append({
                    'opponent': opponent.username,  # ✅ Récupère le `username`
                    'result': 'win' if match.winner == user else 'loss',
                    'score_user': match.score_left if match.game.player_left == user else match.score_right,
                    'score_opponent': match.score_right if match.game.player_left == user else match.score_left,
                    'played_at': match.ended_at,
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
