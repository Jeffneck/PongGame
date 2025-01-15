# game/forms.py

from django import forms
from .models import GameParameters

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
