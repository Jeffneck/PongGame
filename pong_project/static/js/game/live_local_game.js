// live_local_game.js
import { initLiveGame } from './live_game_utils.js'; // Adjust path

import { requestPost } from '../api/index.js';

export function liveLocalGame(options) {
  const { gameId, resultsUrl = '/results' } = options;

  // 1) Définir la callback pour "Start la partie" (start_local_game)
  async function startGameLocal(gameId) {
    const url = `start_local_game/${gameId}`;
    const formData = new FormData();
    formData.append('game_id', gameId);

    const response = await requestPost('game', url, formData);
    if (response.status === 'success') {
      alert("La partie va commencer (LOCAL)!");
    } else {
      alert("Erreur lors du démarrage (LOCAL): " + response.message);
    }
  }

  // 2) Construire l'URL du WebSocket
  const protocol = (window.location.protocol === 'https:') ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws/pong/${gameId}/`;

  // 3) Appeler initLiveGame
  initLiveGame({
    gameId,
    userRole: 'both',           // => local => on bouge left + right
    resultsUrl,
    wsUrl,
    startGameSelector: "#startGameBtn",  // le bouton
    onStartGame: startGameLocal         // la callback
  });

  // Rien de plus à faire : tout le reste est géré par initLiveGame
}
