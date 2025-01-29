// live_online_game_left.js
import { initLiveGame } from './live_game_utils.js';
import { requestPost } from '../api/index.js';

export function liveOnlineGameLeft(options) {
  const { gameId, resultsUrl = '/results' } = options;

  // 1) La callback "Start la partie (online) pour LE JOUEUR GAUCHE"
  async function runGameOnlineLeft(gameId) {
    // => Suppose qu'on appelle run_online_game/<gameId> ou start_online_game/<gameId>
    const url = `run_online_game/${gameId}`;
    const formData = new FormData();
    formData.append('game_id', gameId);

    const response = await requestPost('game', url, formData);
    if (response.status === 'success') {
      alert("La partie (online, LEFT) commence!");
    } else {
      alert("Erreur lors du démarrage (online left): " + response.message);
    }
  }

  // 2) WebSocket URL
  const protocol = (window.location.protocol === 'https:') ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws/pong/${gameId}/`;

  // 3) init
  initLiveGame({
    gameId,
    userRole: 'left',   // => on ne gère que w/s
    resultsUrl,
    wsUrl,
    startGameSelector: "#startGameBtn",
    onStartGame: runGameOnlineLeft
  });
}
