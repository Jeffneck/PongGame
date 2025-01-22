# game/forms.py

from django import forms
from .models import GameParameters, LocalTournament, TournamentParameters

class GameParametersForm(forms.ModelForm):
    class Meta:
        model = GameParameters
        fields = ['ball_speed', 'racket_size', 'bonus_malus_activation', 'bumpers_activation']
        widgets = {
            'ball_speed': forms.Select(attrs={'class': 'form-control'}),
            'racket_size': forms.Select(attrs={'class': 'form-control'}),
            'bonus_malus_activation': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'bumpers_activation': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'ball_speed': 'Vitesse de la balle',
            'racket_size': 'Taille de la raquette',
            'bonus_malus_activation': 'Activer les bonus/malus',
            'bumpers_activation': 'Activer les bumpers/obstacles',
        }

# class LocalTournamentForm(forms.ModelForm):
#     class Meta:
#         model = LocalTournament
#         fields = ['name', 'player1', 'player2', 'player3', 'player4']
#         labels = {
#             'name': 'Nom du Tournoi',
#             'player1': 'Pseudo joueur 1',
#             'player2': 'Pseudo joueur 2',
#             'player3': 'Pseudo joueur 3',
#             'player4': 'Pseudo joueur 4',
#         }
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control'}),
#             'player1': forms.TextInput(attrs={'class': 'form-control'}),
#             'player2': forms.TextInput(attrs={'class': 'form-control'}),
#             'player3': forms.TextInput(attrs={'class': 'form-control'}),
#             'player4': forms.TextInput(attrs={'class': 'form-control'}),
#         }

class LocalTournamentForm(forms.ModelForm):
    # Champs "injectés" depuis GameParameters
    ball_speed = forms.ChoiceField(
        choices=GameParameters.BALL_SPEED_CHOICES,
        label='Vitesse de la balle',
        initial=2
    )
    racket_size = forms.ChoiceField(
        choices=GameParameters.RACKET_SIZE_CHOICES,
        label='Taille de la raquette',
        initial=2
    )
    bonus_malus_activation = forms.BooleanField(
        label='Activer bonus/malus',
        required=False,
        initial=True
    )
    bumpers_activation = forms.BooleanField(
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
                racket_size=self.cleaned_data['racket_size'],
                bonus_malus_activation=self.cleaned_data['bonus_malus_activation'],
                bumpers_activation=self.cleaned_data['bumpers_activation'],
            )
            tournament.parameters = tp
            tournament.save()

        return tournament