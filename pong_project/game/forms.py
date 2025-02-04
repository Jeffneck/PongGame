# game/forms.py

from django import forms
from django.core.exceptions import ValidationError
from .models import GameParameters, LocalTournament, TournamentParameters

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

class TournamentParametersForm(forms.ModelForm):
    # Champs relatifs aux paramètres
    BALL_SPEED_CHOICES = [(1, 'Slow'), (2, 'Medium'), (3, 'Fast')]
    PADDLE_SIZE_CHOICES = [(1, 'Small'), (2, 'Medium'), (3, 'Large')]

    ball_speed = forms.ChoiceField(choices=BALL_SPEED_CHOICES, initial=2, label="Vitesse de balle")
    paddle_size = forms.ChoiceField(choices=PADDLE_SIZE_CHOICES, initial=2, label="Taille raquette")
    bonus_enabled = forms.BooleanField(initial=True, required=False, label="Activer bonus")
    obstacles_enabled = forms.BooleanField(initial=False, required=False, label="Activer obstacles")

    class Meta:
        model = LocalTournament
        fields = ['name', 'player1', 'player2', 'player3', 'player4']
        labels = {
            'name': 'Nom du Tournoi',
            'player1': 'Joueur 1',
            'player2': 'Joueur 2',
            'player3': 'Joueur 3',
            'player4': 'Joueur 4',
        }

    def clean(self):
        cleaned_data = super().clean()
        player1 = cleaned_data.get('player1')
        player2 = cleaned_data.get('player2')
        player3 = cleaned_data.get('player3')
        player4 = cleaned_data.get('player4')

        if (
            player1 == player2 or
            player1 == player3 or
            player1 == player4 or
            player2 == player3 or
            player2 == player4 or
            player3 == player4
        ):
            raise ValidationError("Les noms des joueurs doivent être uniques.")

        return cleaned_data

    def save(self, commit=True):
        tournament = super().save(commit=commit)

        # 2) Crée le TournamentParameters associé
        if commit:
            TournamentParameters.objects.create(
                tournament=tournament,
                ball_speed=self.cleaned_data['ball_speed'],
                paddle_size=self.cleaned_data['paddle_size'],
                bonus_enabled=self.cleaned_data['bonus_enabled'],
                obstacles_enabled=self.cleaned_data['obstacles_enabled'],
            )

        return tournament