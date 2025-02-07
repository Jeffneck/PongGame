# ---- Imports standard ----
import logging
import hashlib  # N'oubliez pas d'importer hashlib si ce n'est pas déjà fait

# ---- Imports tiers ----
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import logout
from accounts.models import RefreshToken
from pong_project.decorators import login_required_json
from django.utils.translation import gettext as _  # Import pour la traduction

# ---- Configuration ----
logger = logging.getLogger(__name__)

@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class LogoutView(View):
    """
    Vue pour gérer la déconnexion utilisateur.
    """
    def post(self, request):
        try:
            logger.debug("Début de la déconnexion")
            raw_refresh_token = request.POST.get('refresh_token')
            if not raw_refresh_token:
                logger.error("Aucun refresh token fourni")
                return JsonResponse({'error': _("Refresh token is required")}, status=400)
            
            # Calculer le hash SHA-256 du refresh token fourni par le client
            hashed_refresh_token = hashlib.sha256(raw_refresh_token.encode('utf-8')).hexdigest()
            
            token = RefreshToken.objects.filter(token=hashed_refresh_token).first()
            if token:
                logger.debug("Token trouvé, suppression...")
                token.delete()
            else:
                logger.error("Refresh token invalide")
                return JsonResponse({'error': _("Invalid refresh token")}, status=401)
            
            logout(request)
            logger.debug("Utilisateur déconnecté")
            return JsonResponse({'status': 'success', 'message': _('Déconnexion réussie.')})
        
        except Exception as e:
            logger.error(f"Erreur lors de la déconnexion : {str(e)}")
            return JsonResponse({'error': _(str(e))}, status=500)
