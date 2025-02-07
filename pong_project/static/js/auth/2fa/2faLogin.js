"use strict";
import { requestPost, requestGet } from '../../api/index.js';
import { handleNavbar } from '../../navbar/index.js';
import { updateHtmlContent, showStatusMessage } from '../../tools/index.js';
import { navigateTo } from '../../router.js';
import { HTTPError } from '../../api/index.js';

async function submitLogin2FA(form) {
  const formData = new FormData(form);
  try {
    const response = await requestPost('accounts', '2fa/login2fa', formData);
    if (response.status === 'success') {
      console.debug("Connexion 2FA réussie.");
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      setTimeout(async () => {
        window.isAuthenticated = true;
        await handleNavbar();
        navigateTo('/home');
      }, 500);
      showStatusMessage('Connexion 2FA réussie.', 'success');
    } else {
      throw new Error(response.message || 'Code 2FA incorrect.');
    }
  } catch (error) {
    console.error('Erreur lors de la soumission 2FA:', error);
    showStatusMessage(error.message || 'Erreur lors de la connexion 2FA.', 'error');
  }
}

export async function initializeLogin2FAView() {
  try {
    const data = await requestGet('accounts', '2fa/login2fa');
    updateHtmlContent('#content', data.html);
  } catch (error) {
    if (error instanceof HTTPError && error.status === 403) {
      showStatusMessage('Vous êtes déjà connecté. Redirection...', 'error');
      navigateTo('/home');
      return;
    }
    console.error('Erreur dans initializeLogin2FAView:', error);
    showStatusMessage('Impossible de charger la vue de connexion 2FA.', 'error');
    return;
  }

  document.addEventListener('submit', (e) => {
    if (e.target && e.target.id === 'login-2fa-form') {
      e.preventDefault();
      submitLogin2FA(e.target);
    }
  });
}
