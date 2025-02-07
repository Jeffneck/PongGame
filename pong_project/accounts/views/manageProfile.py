# ---- Imports standard ----
import logging

# ---- Imports tiers ----
from django.template.loader import render_to_string
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from pong_project.decorators import login_required_json
from django.db.models import Max
from django.contrib.auth import update_session_auth_hash, logout
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

# ---- Imports locaux ----
from accounts.forms import UserNameForm, PasswordChangeForm, AvatarUpdateForm, DeleteAccountForm


# ---- Configuration ----
logger = logging.getLogger(__name__)
User = get_user_model()

@method_decorator(csrf_protect, name='dispatch')  # Applique la protection CSRF à toutes les méthodes de la classe
@method_decorator(login_required_json, name='dispatch')  # Restreint l'accès à la vue aux utilisateurs connectés
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

@method_decorator(csrf_protect, name='dispatch')  # Applique la protection CSRF à toutes les méthodes de la classe
@method_decorator(login_required_json, name='dispatch')  # Restreint l'accès à la vue aux utilisateurs connectés
class ChangeUsernameView(View):
    def post(self, request):
        user = request.user
        form = UserNameForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': _("Nom d'utilisateur mis à jour avec succès.")})
        else:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(error)
            error_message = " ".join(error_messages)
            return JsonResponse({'status': 'error', 'message': error_message})

@method_decorator(csrf_protect, name='dispatch')  # Applique la protection CSRF à toutes les méthodes de la classe
@method_decorator(login_required_json, name='dispatch')  # Restreint l'accès à la vue aux utilisateurs connectés
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
            return JsonResponse({'status': 'success', 'message': _('Votre compte a été supprimé avec succès.')})
        else:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(error)
            error_message = " ".join(error_messages)
            return JsonResponse({'status': 'error', 'message': error_message})

@method_decorator(csrf_protect, name='dispatch')  # Applique la protection CSRF à toutes les méthodes de la classe
@method_decorator(login_required_json, name='dispatch')  # Restreint l'accès à la vue aux utilisateurs connectés
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
            return JsonResponse({'status': 'success', 'message': _('Mot de passe mis à jour avec succès.')})
        
        else:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(error)
            error_message = " ".join(error_messages)
            return JsonResponse({'status': 'error', 'message': error_message})

@method_decorator(csrf_protect, name='dispatch')  # Applique la protection CSRF à toutes les méthodes de la classe
@method_decorator(login_required_json, name='dispatch')  # Restreint l'accès à la vue aux utilisateurs connectés
class UpdateAvatarView(View):
    """
    Handle avatar updates.
    """
    def post(self, request):
        user = request.user
        form = AvatarUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'status': 'success', 
                'message': _('Avatar mis à jour avec succès.')
            })
        else:
            logger.error(form.errors)
            # Récupérer les messages d'erreur de façon plus lisible
            error_messages = []
            for field, errors in form.errors.items():
                # Chaque "errors" est une liste de messages pour le champ "field"
                for error in errors:
                    error_messages.append(error)
            # On peut joindre les messages avec un séparateur, par exemple une virgule ou un saut de ligne
            error_message = " ".join(error_messages)
            
            return JsonResponse({
                'status': 'error', 
                'message': error_message
            })
