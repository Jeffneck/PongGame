# ---- Imports standard ----
import logging

# ---- Imports tiers ----
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from accounts.models import RefreshToken

# ---- Configuration ----
logger = logging.getLogger(__name__)


#@method_decorator(csrf_protect, name='dispatch')  # Applique la protection CSRF à toutes les méthodes de la classe
@method_decorator(login_required, name='dispatch')  # Restreint l'accès à la vue aux utilisateurs connectés
class LogoutView(View):
    """
    Class-Based View (CBV) pour gérer la déconnexion utilisateur.
    - POST : Déconnecte l'utilisateur en mettant à jour son état et en supprimant sa session.
    """

    def post(self, request):
        try:
            logger.debug("Début de la déconnexion")
            refresh_token = request.POST.get('refresh_token')
            if not refresh_token:
                logger.error("Aucun refresh token fourni")
                return JsonResponse({'error': 'Refresh token is required'}, status=400)

            token = RefreshToken.objects.filter(token=refresh_token).first()
            if token:
                logger.debug("Token trouvé, suppression...")
                token.delete()
            else:
                logger.error("Refresh token invalide")
                return JsonResponse({'error': 'Invalid refresh token'}, status=401)

            logout(request)
            logger.debug("Utilisateur déconnecté")
            return JsonResponse({'status': 'success', 'message': 'Déconnexion réussie.'})

        except Exception as e:
            logger.error(f"Erreur lors de la déconnexion : {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
