// live_online_game_right.js
import { initLiveGame } from './live_game_utils.js';

export function liveOnlineGameRight(options) {
  const { gameId, resultsUrl = '/results' } = options;

  // Ici, le joueur de droite n'a pas de bouton "startGame" 
  // => onStartGame : null

  // 1) WebSocket URL
  const protocol = (window.location.protocol === 'https:') ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws/pong/${gameId}/`;

  // 2) init
  initLiveGame({
    gameId,
    userRole: 'right',  // => bouge la raquette "right" (flèches)
    resultsUrl,
    wsUrl,
    // Pas de startGameSelector, pas de callback => le bouton n'existera même pas
  });
}
