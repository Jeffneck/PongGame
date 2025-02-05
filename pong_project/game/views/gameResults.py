from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from game.models import GameSession, GameResult


#affiche une page de resultats avec le winner le score et un bouton retour
@method_decorator(csrf_protect, name='dispatch')
class GameResultsView(View):
    """
    Renvoie les résultats sous forme de JSON (utile pour afficher une page ou des infos de résultats).
    """
    def get(self, request, game_id):
        try:
            session = GameSession.objects.get(id=game_id)
            if(session.status != 'finished'):
                print(f"[ERROR] pas de finish")
                return JsonResponse({
                'status': 'error',
                'message': "La session de jeu n' est pas terminée"
            }, status=401)

            results = GameResult.objects.get(game=session)

            rendered_html = render_to_string('game/game_results.html', {
                'game_id': session.id,
                'winner': results.winner_local if results.winner_local else results.winner.username,
                'looser': results.looser_local if results.looser_local else results.looser.username,
                'score_left': results.score_left,
                'score_right': results.score_right,
            }, request=request)

            print("ON RENVOIE LA PAGE HTML RESULT")
            return JsonResponse({
                'status': 'success',
                'html': rendered_html,
                'winner': results.winner_local if results.winner_local else results.winner.username,
                'looser': results.looser_local if results.looser_local else results.looser.username,
                'score_left': results.score_left,
                'score_right': results.score_right,
            })

        except GameSession.DoesNotExist:
            print(f"[ERROR] pas de session")
            
            return JsonResponse({
                'status': 'error',
                'message': "La session de jeu demandée n'existe pas"
            }, status=404)

        except GameResult.DoesNotExist:
            print(f"[ERROR] pas de result")

            return JsonResponse({
                'status': 'error',
                'message': "Les résultats pour cette session de jeu ne sont pas disponibles"
            }, status=404)

        except Exception as e:
            print(f"[ERROR] {e}")
            return JsonResponse({
                'status': 'error',
                'message': "Une erreur est survenue lors de la récupération des résultats"
            }, status=500)