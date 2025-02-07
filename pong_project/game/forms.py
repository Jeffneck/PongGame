# # game/forms.py

# from django import forms
# from django.core.exceptions import ValidationError
# from .models import GameParameters, LocalTournament, TournamentParameters

# class GameParametersForm(forms.ModelForm):
#     class Meta:
#         model = GameParameters
#         fields = ['ball_speed', 'paddle_size', 'bonus_enabled', 'obstacles_enabled']
#         widgets = {
#             'ball_speed': forms.Select(attrs={'class': 'form-control'}),
#             'paddle_size': forms.Select(attrs={'class': 'form-control'}),
#             'bonus_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#             'obstacles_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#         }
#         labels = {
#             'ball_speed': 'Vitesse de la balle',
#             'paddle_size': 'Taille de la raquette',
#             'bonus_enabled': 'Activer les bonus/malus',
#             'obstacles_enabled': 'Activer les bumpers/obstacles',
#         }

# class TournamentParametersForm(forms.ModelForm):
#     # Champs relatifs aux paramètres
#     BALL_SPEED_CHOICES = [(1, 'Slow'), (2, 'Medium'), (3, 'Fast')]
#     PADDLE_SIZE_CHOICES = [(1, 'Small'), (2, 'Medium'), (3, 'Large')]

#     ball_speed = forms.ChoiceField(choices=BALL_SPEED_CHOICES, initial=2, label="Vitesse de balle")
#     paddle_size = forms.ChoiceField(choices=PADDLE_SIZE_CHOICES, initial=2, label="Taille raquette")
#     bonus_enabled = forms.BooleanField(initial=True, required=False, label="Activer bonus")
#     obstacles_enabled = forms.BooleanField(initial=False, required=False, label="Activer obstacles")

#     class Meta:
#         model = LocalTournament
#         fields = ['name', 'player1', 'player2', 'player3', 'player4']
#         labels = {
#             'name': 'Nom du Tournoi',
#             'player1': 'Joueur 1',
#             'player2': 'Joueur 2',
#             'player3': 'Joueur 3',
#             'player4': 'Joueur 4',
#         }

#     def clean(self):
#         cleaned_data = super().clean()
#         player1 = cleaned_data.get('player1')
#         player2 = cleaned_data.get('player2')
#         player3 = cleaned_data.get('player3')
#         player4 = cleaned_data.get('player4')

#         if (
#             player1 == player2 or
#             player1 == player3 or
#             player1 == player4 or
#             player2 == player3 or
#             player2 == player4 or
#             player3 == player4
#         ):
#             raise ValidationError("Les noms des joueurs doivent être uniques.")

#         return cleaned_data

#     def save(self, commit=True):
#         tournament = super().save(commit=commit)

#         # 2) Crée le TournamentParameters associé
#         if commit:
#             TournamentParameters.objects.create(
#                 tournament=tournament,
#                 ball_speed=self.cleaned_data['ball_speed'],
#                 paddle_size=self.cleaned_data['paddle_size'],
#                 bonus_enabled=self.cleaned_data['bonus_enabled'],
#                 obstacles_enabled=self.cleaned_data['obstacles_enabled'],
#             )

#         return tournament


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

    def clean(self):
        # Vous pouvez ajouter ici d'éventuelles validations supplémentaires si nécessaire
        cleaned_data = super().clean()
        # Par exemple, on pourrait vérifier que ball_speed et paddle_size sont des valeurs attendues (les choix le garantissent déjà)
        return cleaned_data


class TournamentParametersForm(forms.ModelForm):
    # Définition des choix pour les paramètres de tournoi
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
        """
        Nettoie et valide que les noms de joueurs sont uniques, en supprimant les espaces en début/fin.
        """
        cleaned_data = super().clean()
        player1 = (cleaned_data.get('player1') or "").strip()
        player2 = (cleaned_data.get('player2') or "").strip()
        player3 = (cleaned_data.get('player3') or "").strip()
        player4 = (cleaned_data.get('player4') or "").strip()

        # Affecte les valeurs nettoyées dans cleaned_data
        cleaned_data['player1'] = player1
        cleaned_data['player2'] = player2
        cleaned_data['player3'] = player3
        cleaned_data['player4'] = player4

        players = [player1, player2, player3, player4]
        if len(set(players)) != 4:
            raise ValidationError("Les noms des joueurs doivent être uniques.")
        return cleaned_data

    def save(self, commit=True):
        """
        Enregistre le tournoi et crée les TournamentParameters associés.
        """
        tournament = super().save(commit=commit)
        if commit:
            TournamentParameters.objects.create(
                tournament=tournament,
                ball_speed=self.cleaned_data['ball_speed'],
                paddle_size=self.cleaned_data['paddle_size'],
                bonus_enabled=self.cleaned_data['bonus_enabled'],
                obstacles_enabled=self.cleaned_data['obstacles_enabled'],
            )
        return tournament
