"use strict";
import { requestGet } from '../api/index.js';
import { isTouchDevice } from '../tools/utility.js';
import { updateHtmlContent } from '../tools/domHandler.js';
import { initializeGameControls } from './controls.js';
import { displayGame, displayTournamentBracket } from './display.js';

export async function startLoading(participantCount) {
  try {
    const response = await requestGet('game', 'loading');
    updateHtmlContent('#content', response.html);
    if (isTouchDevice()) {
      initializeGameControls('touch');
    } else {
      initializeGameControls('keyboard');
    }
    // Vous pouvez activer le polling ou le déclenchement d'une action après un délai ici si nécessaire.
  } catch (error) {
    console.error('Erreur dans startLoading:', error);
  }
}
