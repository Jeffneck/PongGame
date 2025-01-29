# game/forms.py

from django import forms
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

# class SendInvitationForm(forms.ModelForm):
#     """
#     Formulaire pour envoyer une invitation et stocker
#     les paramètres dans GameInvitationParameters.
#     """
#     friend_username = forms.CharField(
#         required=True,
#         label="Nom d'utilisateur de l'ami à inviter"
#     )

#     class Meta:
#         model = GameInvitationParameters
#         fields = [
#             'ball_speed', 
#             'paddle_size',
#             'bonus_enabled',
#             'obstacles_enabled'
#         ]


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


# added (utilisable plus tard pour recuperer le nom des joueurs d'une partie locale plutot que de les nommer player_left par defaut .. etc)
# class LocalGameForm(forms.Form):
#     """
#     Formulaire pour récupérer les noms des joueurs pour une partie locale.
#     """
#     player_left_name = forms.CharField(max_length=50, required=True, label="Nom du joueur gauche")
#     player_right_name = forms.CharField(max_length=50, required=True, label="Nom du joueur droit")

#     def clean_player_left_name(self):
#         player_left_name = self.cleaned_data.get('player_left_name')
#         if len(player_left_name.strip()) == 0:
#             raise forms.ValidationError("Le nom du joueur gauche ne peut pas être vide.")
#         return player_left_name

#     def clean_player_right_name(self):
#         player_right_name = self.cleaned_data.get('player_right_name')
#         if len(player_right_name.strip()) == 0:
#             raise forms.ValidationError("Le nom du joueur droit ne peut pas être vide.")
#         return player_right_name
# VUE ADAPTEE A CE FORMULAIRE
# class CreateGameLocalView(View):
#     """
#     Gère la création d'une nouvelle GameSession et des paramètres associés pour une partie locale.
#     """
#     def post(self, request):
#         # Formulaire des paramètres du jeu
#         game_parameters_form = GameParametersForm(request.POST)
        
#         # Formulaire des noms des joueurs
#         game_session_form = GameSessionForm(request.POST)

#         if not game_parameters_form.is_valid() or not game_session_form.is_valid():
#             # Si l'un des formulaires n'est pas valide, retourner une réponse d'erreur
#             return JsonResponse({
#                 'status': 'error',
#                 'message': "Les paramètres du jeu ou les noms des joueurs sont invalides."
#             })

#         # Créer une nouvelle GameSession pour une partie locale
#         session = GameSession.objects.create(status='waiting', is_online=False)

#         # Récupérer les noms des joueurs depuis le formulaire
#         player_left_name = game_session_form.cleaned_data['player_left_name']
#         player_right_name = game_session_form.cleaned_data['player_right_name']

#         # Assigner les noms des joueurs à la session
#         session.player_left_name = player_left_name
#         session.player_right_name = player_right_name
#         session.save()

#         # Créer les paramètres de jeu associés à cette session
#         parameters = game_parameters_form.save(commit=False)
#         parameters.game_session = session
#         parameters.save()

#         # Log de la création de la session de jeu
#         print(f"[create_game] GameSession {session.id} créée pour les joueurs {player_left_name} et {player_right_name} avec paramètres personnalisés.")

#         # Réponse JSON indiquant que la partie a été créée avec succès
#         return JsonResponse({
#             'status': 'success',
#             'message': "Partie locale créée avec succès.",
#             'game_id': str(session.id)
#         }, status=201)