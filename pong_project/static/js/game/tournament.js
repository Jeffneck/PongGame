import { requestGet, requestPost } from "../api/index.js";
import { updateHtmlContent } from "../tools/index.js";
import { showStatusMessage } from "../tools/index.js";
import { initLiveGame } from './live_game_utils.js'; // Adjust path

export async function handleTournament(tournamentParam) {
  // Effectuer une requête GET pour récupérer le formulaire
  const responseGet = await requestGet('game', 'create_tournament');

  if (responseGet.status === 'success') {
      updateHtmlContent('#content', responseGet.html);
  }

  // Sélectionner le formulaire après l'injection du HTML
  const form = document.querySelector('#content form');
  if (!form) {
      console.error("Formulaire introuvable.");
      return;
  }

  // Ajouter un écouteur d'événement sur le formulaire pour capturer la soumission
  form.addEventListener("submit", async function (event) {
      event.preventDefault();  // Empêcher le rechargement de la page

      const formData = new FormData(form);

      // Ajouter les paramètres du tournoi s'ils existent
      if (tournamentParam) {
          formData.append('ball_speed', tournamentParam.ball_speed);
          formData.append('paddle_size', tournamentParam.paddle_size);
          formData.append('bonus_enabled', tournamentParam.bonus_enabled);
          formData.append('obstacles_enabled', tournamentParam.obstacles_enabled);
      }
      const tournamentName = document.getElementById(`tournament-name`);
      const player1 = document.getElementById(`player1`);
      const player2 = document.getElementById(`player2`);
      const player3 = document.getElementById(`player3`);
      const player4 = document.getElementById(`player4`);

      formData.append('name', tournamentName);
      formData.append('player1', player1);
      formData.append('player2', player2);
      formData.append('player3', player3);
      formData.append('player4', player4);
      

      try {
          // Envoyer la requête POST
          const response = await requestPost('game', 'create_tournament', formData);
          
          if (response.status === 'success') {
              alert(`Tournoi créé avec succès : ID = ${response.tournament_id}`);
              updateHtmlContent('#content', response.html);
              tournamentLoop(response.tournament_id);
          } else {
              alert(response.message);
          }
      } catch (error) {
          console.error("Erreur lors de la soumission du formulaire :", error);
          alert("Une erreur est survenue lors de la création du tournoi.");
      }
  });
}

async function tournamentLoop(tournament_id) {
  while (true) {
      // Récupérer le contexte du tournoi
      const responseGet = await requestGet('game', `extract_tournament/${tournament_id}`);
      
      if (!responseGet || responseGet.status !== "success") {
          console.error("Impossible de récupérer le contexte du tournoi.");
          return;
      }

      // Vérifier si le tournoi est terminé
      if (responseGet.tournament_context.tournament_status === "finished") {
          console.log("Tournoi terminé.");
          break;
      }

      // Afficher le bracket pendant 4 secondes
      updateHtmlContent("#content", responseGet.html);
      await delay(4000);

      // Afficher les joueurs qui s'affrontent pendant 3 secondes
      const nextGameResponse = await requestGet('game', `tournament_next_game/${tournament_id}`);

      if (!nextGameResponse || nextGameResponse.status !== "success") {
          console.error("Impossible de récupérer les joueurs du prochain match.");
          return;
      }

      updateHtmlContent("#content", nextGameResponse.html);
      await delay(3000);

      // Créer une nouvelle session de jeu et récupérer la `game_id`
      const game_id = await createTournamentGameSession(tournament_id);

      if (game_id) {
          liveTournamentGame(game_id); // Lancer la partie
      } else {
          console.error("Erreur lors de la création de la session de match.");
          return;
      }
  }
}

// Fonction utilitaire pour créer une pause asynchrone
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
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
