# ---- Imports standard ----
import logging

# ---- Imports tiers ----
from django.template.loader import render_to_string
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.db.models import Max
from django.contrib.auth import update_session_auth_hash, logout
from django.contrib.auth import get_user_model

# ---- Imports locaux ----
from accounts.forms import UserNameForm, PasswordChangeForm, AvatarUpdateForm, DeleteAccountForm


# ---- Configuration ----
logger = logging.getLogger(__name__)
User = get_user_model()


class ManageProfileView(View):
    """
    Display and manage profile-related forms.
    """

    def get(self, request):
        user = request.user
        profile_form = UserNameForm(instance=user)
        password_form = PasswordChangeForm(user=user)
        avatar_form = AvatarUpdateForm(instance=user)
        delete_form = DeleteAccountForm(user=user)
        # Render HTML as a string
        rendered_html = render_to_string('accounts/gestion_profil.html', {
            'profile_form': profile_form,
            'password_form': password_form,
            'avatar_form': avatar_form,
            'delete_form': delete_form,
            'profile_user': user,
        })

        return JsonResponse({
            'status': 'success',
            'html': rendered_html
        })


class UpdateProfileView(View):
    """
    Handle updates to user profile information.
    """

    def post(self, request):
        user = request.user
        form = UserNameForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': 'Profil mis à jour avec succès.'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})


class DeleteAccountView(View):
    """
    Handle account deletion.
    """

    def post(self, request):
        user = request.user
        form = DeleteAccountForm(user, data=request.POST)
        if form.is_valid():
            logout(request)
            user.delete()
            return JsonResponse({'status': 'success', 'message': 'Votre compte a été supprimé avec succès.'})
        else:
            return JsonResponse({'status': 'error', 'message': form.errors['password'][0]}, status=400)

class ChangePasswordView(View):
    """
    Handle password changes using Django's built-in functions.
    """

    def post(self, request):
        user = request.user  # Récupérer l'utilisateur authentifié
        form = PasswordChangeForm(user, request.POST)  # Formulaire standard pour changer le mot de passe

        if form.is_valid():
            # Met à jour le mot de passe et hache automatiquement
            form.save()
            update_session_auth_hash(request, user)  # Maintient la session active après la mise à jour
            return JsonResponse({'status': 'success', 'message': 'Mot de passe mis à jour avec succès.'})

        # Retourner les erreurs si le formulaire est invalide
        return JsonResponse({'status': 'error', 'errors': form.errors})


class UpdateAvatarView(View):
    """
    Handle avatar updates.
    """
    def post(self, request):
        user = request.user
        form = AvatarUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': 'Avatar mis à jour avec succès.'})
        return JsonResponse({'status': 'error', 'errors': form.errors})
