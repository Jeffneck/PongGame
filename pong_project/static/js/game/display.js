"use strict";
import { requestGet } from '../api/index.js';
import { resetScrollPosition } from '../tools/utility.js';
import { updateHtmlContent } from '../tools/domHandler.js';

export async function displayGame() {
  try {
    const response = await requestGet('game', 'game');
    document.querySelector('#home').innerHTML = response.html || response;
    resetScrollPosition();
  } catch (error) {
    console.error('Erreur lors du chargement du jeu:', error);
  }
}

export async function displayTournamentBracket(participantCount) {
  const url = participantCount === 4 ? 'bracket_4.html' : 'bracket_8.html';
  try {
    const response = await Api.get(url);
    document.querySelector('#home').innerHTML = response.html || response;
    resetScrollPosition();
  } catch (error) {
    console.error('Erreur lors du chargement du bracket:', error);
  }
}
