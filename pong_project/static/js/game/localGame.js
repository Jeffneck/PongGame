"use strict";
import { requestGet, requestPost } from "../api/index.js";
import { updateHtmlContent, showStatusMessage } from "../tools/index.js";
import { launchLiveGameWithOptions } from "./live_game.js";
import { showResults } from "./gameResults.js";

export async function handleLocalGame(parametersForm) {
  try {
    const response = await requestPost('game', 'create_local_game', parametersForm);
    if (response.status === 'success') {
      showStatusMessage(`Partie créée : ID = ${response.game_id}`, 'success');
      updateHtmlContent('#content', response.html);
      const gameId = response.game_id;
      await launchLiveGameWithOptions(gameId, 'both', `start_local_game/${gameId}`);
      await showResults(gameId);
    } else {
      showStatusMessage(response.message, 'error');
    }
  } catch (err) {
    console.error('Erreur dans handleLocalGame:', err);
    showStatusMessage('Erreur lors de la création de la partie locale.', 'error');
  }
}
