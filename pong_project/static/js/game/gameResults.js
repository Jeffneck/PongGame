"use strict";
import { requestGet } from "../api/index.js";
import { updateHtmlContent, showStatusMessage } from "../tools/index.js";

export async function showResults(gameId) {
  try {
    const response = await requestGet('game', `game_results/${gameId}`);
    if (response.status === 'success') {
      updateHtmlContent('#content', response.html);
    } else {
      showStatusMessage(response.message, 'error');
    }
  } catch (error) {
    console.error('Erreur dans showResults:', error);
    showStatusMessage('Impossible d\'obtenir les résultats', 'error');
  }
}
