import { requestGet, requestPost } from "../api/index.js";
import { updateHtmlContent } from "../tools/index.js";
import { showStatusMessage } from "../tools/index.js";
import { initLiveGame } from './live_game_utils.js'; // Adjust path

export async function createTournament(tournamentParams) {
    console.log('[createTournament] Paramètres = ', tournamentParams);

    const formData = new FormData();
    if (tournamentParams) {
        formData.append('ball_speed',               tournamentParams.ball_speed);
        formData.append('paddle_size',             tournamentParams.paddle_size);
        formData.append('bonus_enabled',  tournamentParams.bonus_enabled);
        formData.append('obstacles_enabled',      tournamentParams.obstacles_enabled);
        formData.append('player1',      tournamentParams.player1);
        formData.append('player2',      tournamentParams.player2);
        formData.append('player3',      tournamentParams.player3);
        formData.append('player4',      tournamentParams.player4);
    } else {
        console.warn('Aucun paramètre.');
    }
    // Envoi du formulaire contenant les Tournament Parameters à CreateTournamentView
    try {
        const response = await requestPost('game', 'create_tournament', formData);
        console.log('requestPost create_tournament effectuée'); 
        if (response.status === 'success') {
            updateHtmlContent('#content', response.html);
            tournamentLoop(response.tournament_id);
        } else {
            showStatusMessage(response.message, 'error');
        }
    } catch (error) {
            showStatusMessage('Une erreur est survenue.', 'error');
            console.error('Erreur createTournament :', error);
    }
}

async function tournamentLoop(tournament_id){

    // boucler jusqu'a ce que tournament.status soit 'finished'
    // afficher le tournament bracket pendant 4 secondes
    await displayTournamentbracket(tournament_id);
    // afficher une page qui présente les 2 joueurs s'affontant au prochain match pendant 3 secondes
    // affichage différent en fonction du match_type pour les semifinals et des 2 winners des semifinals pour la finale
    await displayNextGamePlayers(tournament_id);
    // identifier la bonne gamesession en fonction du status du tournoi
    CreateTournamentGameSession() //retourne la game_id dans 
}

async function CreateTournamentGameSession(tournament_id)
{
    // appel a la view CreateTournamentGameSession() pour creer la nouvelle game session 

    // si la view retourne response.success on lance la game
    liveTournamentGame(game_id)
}



function liveTournamentGame(game_id) {

  // 1) Définir la callback pour "Start la partie" (start_Tournament_game)
  async function startTournamentGame(gameId) {
    const url = `start_Tournament_game/${gameId}`;
    const formData = new FormData();
    formData.append('game_id', gameId);

    const response = await requestPost('game', url, formData);
    if (response.status === 'success') {
      alert("La partie va commencer (Tournament)!");
    } else {
      alert("Erreur lors du démarrage (Tournament): " + response.message);
    }
  }

  // 2) Construire l'URL du WebSocket
  const protocol = (window.location.protocol === 'https:') ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws/pong/${gameId}/`;

  // 3) Appeler initLiveGame
  initLiveGame({
    gameId,
    userRole: 'both',           // => Tournament = Local Game => on bouge left + right
    resultsUrl,
    wsUrl,
    startGameSelector: "#startGameBtn",  // le bouton
    onStartGame: startTournamentGame         // la callback
  });
}
