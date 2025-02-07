"use strict";
import { updateHtmlContent } from '../tools/index.js';
import { requestGet } from '../api/index.js';
import { navigateTo } from '../router.js';
import { showStatusMessage } from '../tools/index.js';

export async function initializeGameHomeView() {
  try {
    console.debug('Initialisation de GameHomeView');
    const data = await requestGet('game', 'home');
    if (data && data.html) {
      updateHtmlContent('#content', data.html);
    } else {
      showStatusMessage('Données HTML manquantes pour GameHomeView.', 'error');
    }
  } catch (error) {
    console.error('Erreur dans initializeGameHomeView:', error);
    showStatusMessage('Erreur lors du chargement de la page d\'accueil du jeu.', 'error');
  }
  const playBtn = document.querySelector('#play-btn-home');
  if (!playBtn) {
    showStatusMessage('Bouton "Jouer" introuvable.', 'error');
    return;
  }
  if (!playBtn.dataset.bound) {
    playBtn.addEventListener('click', (e) => {
      e.preventDefault();
      navigateTo('/game-options');
    });
    playBtn.dataset.bound = true;
  }
}
