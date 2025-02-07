"use strict";
import { isTouchDevice } from "../tools/index.js";
import { requestPost } from "../api/index.js";
import { updateHtmlContent } from "../tools/domHandler.js";
import { launchLiveGameWithOptions } from "./live_game.js";
import { showResults } from "./gameResults.js";

export async function launchLiveGameWithOptions(gameId, userRole, urlStartButton) {
  try {
    const protocol = (window.location.protocol === 'https:') ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/pong/${gameId}/`;
    const startGameSelector = document.querySelector("#startGameBtn") || null;
    let onStartGame = null;
    if (urlStartButton && startGameSelector) {
      onStartGame = async () => {
        startGameSelector.classList.add('d-none');
        const formData = new FormData();
        formData.append('game_id', gameId);
        formData.append('userRole', userRole);
        const response = await requestPost('game', urlStartButton, formData);
        if (response.status !== 'success') {
          alert("Erreur lors du démarrage : " + response.message);
        }
      };
    }
    return initLiveGame({ gameId, userRole, wsUrl, startGameSelector, onStartGame });
  } catch (error) {
    console.error("Erreur dans launchLiveGameWithOptions :", error);
    throw error;
  }
}

// ... (Les fonctions graphiques telles que initPowerupImages, createSpawnEffect, createCollisionEffect, etc.)
// Assurez-vous d'encapsuler les blocs de code critiques dans try/catch si nécessaire.
