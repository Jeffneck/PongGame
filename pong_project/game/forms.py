# game/forms.py

from django import forms
from .models import GameParameters, LocalTournament

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

class LocalTournamentForm(forms.ModelForm):
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