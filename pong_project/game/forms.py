# game/forms.py

from django import forms
from .models import GameParameters, LocalTournament, TournamentParameters, GameInvitationParameters

class GameParametersForm(forms.ModelForm):
    class Meta:
        model = GameParameters
        fields = ['ball_speed', 'paddle_size', 'bonus_enabled', 'obstacles_enabled']
        widgets = {
            'ball_speed': forms.Select(attrs={'class': 'form-control'}),
            'paddle_size': forms.Select(attrs={'class': 'form-control'}),
            'bonus_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'obstacles_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'ball_speed': 'Vitesse de la balle',
            'paddle_size': 'Taille de la raquette',
            'bonus_enabled': 'Activer les bonus/malus',
            'obstacles_enabled': 'Activer les bumpers/obstacles',
        }

class SendInvitationForm(forms.ModelForm):
    """
    Formulaire pour envoyer une invitation et stocker
    les paramètres dans GameInvitationParameters.
    """
    friend_username = forms.CharField(
        required=True,
        label="Nom d'utilisateur de l'ami à inviter"
    )

    class Meta:
        model = GameInvitationParameters
        fields = [
            'ball_speed', 
            'paddle_size',
            'bonus_enabled',
            'obstacles_enabled'
        ]


class LocalTournamentForm(forms.ModelForm):
    # Champs "injectés" depuis GameParameters
    ball_speed = forms.ChoiceField(
        choices=GameParameters.BALL_SPEED_CHOICES,
        label='Vitesse de la balle',
        initial=2
    )
    paddle_size = forms.ChoiceField(
        choices=GameParameters.paddle_size_CHOICES,
        label='Taille de la raquette',
        initial=2
    )
    bonus_enabled = forms.BooleanField(
        label='Activer bonus/malus',
        required=False,
        initial=True
    )
    obstacles_enabled = forms.BooleanField(
        label='Activer bumpers',
        required=False,
        initial=False
    )

    class Meta:
        model = LocalTournament
        fields = ['name', 'player1', 'player2', 'player3', 'player4']
        labels = {
            'name': 'Nom du Tournoi',
            'player1': 'Pseudo joueur 1',
            'player2': 'Pseudo joueur 2',
            'player3': 'Pseudo joueur 3',
            'player4': 'Pseudo joueur 4',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'player1': forms.TextInput(attrs={'class': 'form-control'}),
            'player2': forms.TextInput(attrs={'class': 'form-control'}),
            'player3': forms.TextInput(attrs={'class': 'form-control'}),
            'player4': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        """
        1) Crée le LocalTournament (pseudos, name).
        2) Crée un GameParameters 'temporaire' (sans GameSession) avec 
           les champs provenant du formulaire.
        3) Associe ce GameParameters au LocalTournament.
        """
        tournament = super().save(commit=False)

        if commit:
            # On doit d'abord sauvegarder le LocalTournament
            tournament.save()

            # Créer un GameParameters "isolé" (pas lié à une GameSession)
            tp = TournamentParameters.objects.create(
                ball_speed=self.cleaned_data['ball_speed'],
                paddle_size=self.cleaned_data['paddle_size'],
                bonus_enabled=self.cleaned_data['bonus_enabled'],
                obstacles_enabled=self.cleaned_data['obstacles_enabled'],
            )
            tournament.parameters = tp
            tournament.save()

        return tournament


