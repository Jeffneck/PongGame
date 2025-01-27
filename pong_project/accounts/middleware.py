# ---- Imports standard ----
import logging

# ---- Imports tiers ----
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

# ---- Configuration ----
logger = logging.getLogger(__name__)
User = get_user_model()


class UpdateLastActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            user = request.user
            user.last_activity = timezone.now()
            user.save()
        response = self.get_response(request)
        return response