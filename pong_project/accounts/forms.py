# accounts/forms.py
# ---- Imports standard ----
import logging
import re 
# ---- Imports tiers ----
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm  # Formulaire pour la création d'utilisateur
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.forms.widgets import ClearableFileInput
from django.utils.translation import gettext_lazy as _
from PIL import Image


# ---- Configuration ----
User = get_user_model()
logger = logging.getLogger(__name__)

class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label="Nom d'utilisateur")
    password = forms.CharField(widget=forms.PasswordInput, label='Mot de passe')

class TwoFactorLoginForm(forms.Form):
    code = forms.CharField(max_length=6, min_length=6, label='Code 2FA')

    def clean_code(self):
        code = self.cleaned_data['code']
        if not code.isdigit():
            raise forms.ValidationError("Le code doit contenir uniquement des chiffres")
        return code

class UserNameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Nom d'utilisateur"
            }),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            username = username.strip()
            # Vérifier si le nouveau nom d'utilisateur est identique à l'actuel (insensible à la casse)
            if username.lower() == self.instance.username.lower():
                raise ValidationError(_("Le nouveau nom d'utilisateur doit être différent de l'actuel."))
            # Vérifier que le nom d'utilisateur ne contient que des lettres, chiffres et underscores
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                raise ValidationError(_("Le nom d'utilisateur ne doit contenir que des lettres, chiffres et underscores."))
            # Vérifier l'unicité du nom d'utilisateur (insensible à la casse)
            if User.objects.exclude(id=self.instance.id).filter(username__iexact=username).exists():
                raise ValidationError(_("Ce nom d'utilisateur est déjà pris."))
        else:
            raise ValidationError(_("Le nom d'utilisateur ne peut pas être vide."))
        return username

class PasswordChangeForm(DjangoPasswordChangeForm):
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']

class CustomClearableFileInput(ClearableFileInput):
    """Widget personnalisé pour masquer 'Actuellement' et 'Effacer'."""
    initial_text = ''  # Supprime le texte "Actuellement"
    input_text = _('Choisir un fichier')  # Texte pour le bouton d'upload
    clear_checkbox_label = ''  # Supprime le texte "Effacer"

class AvatarUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar', None)
        if not avatar:
            raise ValidationError(_("Aucun fichier n'a été téléchargé."))
            
        max_size = 4 * 1024 * 1024  # 4 Mo
        if avatar.size > max_size:
            raise ValidationError(_("L'image ne doit pas dépasser 4 Mo."))
            
        allowed_content_types = ["image/jpeg", "image/jpg", "image/png", "image/gif"]
        if avatar.content_type not in allowed_content_types:
            raise ValidationError(_("Seules les images JPEG, JPG, PNG et GIF sont autorisées."))
        
        try:
            # Assurer que le curseur est au début du fichier
            avatar.seek(0)
            image = Image.open(avatar)
            # Charger l'image entièrement pour s'assurer qu'elle est valide
            image.load()
        except Exception as e:
            logger.error("Erreur lors de la vérification de l'image: %s", e)
            raise ValidationError(_("Fichier image invalide ou corrompu."))
        
        # Réinitialiser le curseur pour que Django puisse enregistrer le fichier
        avatar.seek(0)
        return avatar

class DeleteAccountForm(forms.Form):
    password = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput(attrs={'placeholder': _("Entrez votre mot de passe")}),
        label="Mot de passe"
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data['password']
        if not authenticate(username=self.user.username, password=password):
            raise forms.ValidationError(_("Mot de passe incorrect."))
        return password