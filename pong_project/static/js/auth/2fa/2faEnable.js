"use strict";
import { navigateTo } from '/static/js/router.js';
import { requestGet, requestPost } from '/static/js/api/index.js';
import { updateHtmlContent, showStatusMessage } from '/static/js/tools/index.js';

async function loadEnable2FAView() {
  try {
    const response = await requestGet('accounts', '2fa/enable');
    if (!response) return false;
    if (response.status === 'success' && response.html) {
      updateHtmlContent('#content', response.html);
      attach2FAVerificationEvent();
      return true;
    } else {
      throw new Error(response.message || 'Erreur lors du chargement de la vue 2FA.');
    }
  } catch (error) {
    console.error('Erreur lors du chargement de la vue 2FA:', error);
    showStatusMessage('Impossible de charger la vue d\'activation de la 2FA.', 'error');
    throw error;
  }
}

async function verification2FA(event) {
  event.preventDefault();
  console.debug('Soumission du formulaire de vérification 2FA...');
  const form = event.target;
  const formData = new FormData(form);
  try {
    const response = await requestPost('accounts', '2fa/check', formData);
    if (response.status === 'success') {
      showStatusMessage('2FA activée avec succès.', 'success');
      setTimeout(() => {
        navigateTo('/account');
      }, 2000);
    } else {
      throw new Error(response.message || 'Code 2FA incorrect.');
    }
  } catch (error) {
    console.error('Erreur lors de la vérification 2FA:', error);
    showStatusMessage('Erreur lors de la vérification de la 2FA.', 'error');
    throw error;
  }
}

function attach2FAVerificationEvent() {
  const verifyForm = document.querySelector('#verify-2fa-form');
  if (verifyForm) {
    verifyForm.addEventListener('submit', async (event) => {
      try {
        await verification2FA(event);
      } catch (error) {
        console.error('Erreur dans attach2FAVerificationEvent:', error);
        showStatusMessage('Erreur lors de la vérification 2FA.', 'error');
      }
    });
    console.debug('Événement de vérification 2FA attaché.');
  } else {
    console.error('Formulaire de vérification 2FA introuvable.');
    showStatusMessage('Formulaire de vérification introuvable.', 'error');
  }
}

export async function handleEnable2FA() {
  try {
    console.debug('Activation de la 2FA...');
    const loaded = await loadEnable2FAView();
    if (!loaded) return;
  } catch (error) {
    console.error('Erreur dans handleEnable2FA:', error);
    showStatusMessage('Erreur lors de l\'activation de la 2FA.', 'error');
  }
}
