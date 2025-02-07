from django.http import JsonResponse
from functools import wraps

import logging
logger = logging.getLogger(__name__)

def user_not_authenticated(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'Utilisateur déjà connecté'}, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view



def login_required_json(view_func):
    # logger.debug("Entering login_required_json()")
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({
                'status': 'error',
                'message': 'Utilisateur non authentifié',
                "error_code": "forbidden",
                'redirect': '/' # l'URL souhaitée
            }, status=401)
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def auth_partial_required(view_func):
    """
    Vérifie si l'utilisateur a été authentifié partiellement (auth_partial) en vérifiant la variable
    de session 'auth_partial'. Si ce n'est pas le cas, renvoie une réponse JSON indiquant que l'action
    nécessite une authentification partielle (par exemple pour 2FA).
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('auth_partial', False):  # Valeur par défaut à False
            logger.debug("Utilisateur non authentifié partiellement")
            return JsonResponse({
                'status': 'error',
                'message': 'Authentification partielle requise.',
                'error_code': 'auth_partial_required',
                'redirect': '/'
            }, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view
