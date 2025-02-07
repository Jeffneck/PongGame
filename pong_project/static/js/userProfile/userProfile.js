"use strict";
import { requestGet } from '../api/index.js';
import { updateHtmlContent, showStatusMessage } from '../tools/index.js';
import { navigateTo } from '../router.js';

async function viewUserProfile() {
  try {
    const response = await requestGet('accounts', 'userProfile');
    if (!response) return false;
    if (response.status === 'success' && response.html) {
      updateHtmlContent('#content', response.html);
    } else {
      throw new Error(response.message || 'Erreur lors du chargement du profil.');
    }
    return true;
  } catch (error) {
    console.error('Erreur dans viewUserProfile:', error);
    showStatusMessage('Erreur lors du chargement du profil utilisateur.', 'error');
    throw error;
  }
}

async function initializeProfileEvents() {
  try {
    const gestionBtn = document.querySelector('#gestion-btn');
    if (!gestionBtn) {
      throw new Error('Bouton de gestion introuvable.');
    }
    gestionBtn.addEventListener('click', () => navigateTo('/account'));
  } catch (error) {
    console.error("Erreur dans initializeProfileEvents:", error);
    showStatusMessage('Erreur lors de l\'initialisation des événements du profil.', 'error');
    throw error;
  }
}

export async function handleViewProfile() {
  try {
    const loaded = await viewUserProfile();
    if (!loaded) return;
    await initializeProfileEvents();
  } catch (error) {
    console.error('Erreur dans handleViewProfile:', error);
    showStatusMessage('Erreur lors du chargement du profil utilisateur.', 'error');
  }
}
