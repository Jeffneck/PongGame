from django.http import JsonResponse
from functools import wraps

def user_not_authenticated(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'Utilisateur déjà connecté'}, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view