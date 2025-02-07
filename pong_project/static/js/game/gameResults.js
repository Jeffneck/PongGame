"use strict";
import { requestGet } from "../api/index.js";
import { updateHtmlContent, showStatusMessage } from "../tools/index.js";

export async function showResults(gameId) {
  try {
    const response = await requestGet('game', `game_results/${gameId}`);
    if (response.status === 'success') {
      showStatusMessage(`Partie terminée ! Winner: ${response.winner}  Looser: ${response.looser}\nScore: ${response.score_left} - ${response.score_right}`, 'success');
      updateHtmlContent('#content', response.html);
    } else {
      showStatusMessage(response.message, 'error');
    }
  } catch (error) {
    console.error('Erreur dans showResults:', error);
    showStatusMessage('Impossible d\'obtenir les résultats', 'error');
  }
}
