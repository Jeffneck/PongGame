"use strict";
import { requestGet, requestPost } from '../api/index.js';
import { handleNavbar } from '../navbar/index.js';
import { updateHtmlContent, showStatusMessage } from '../tools/index.js';
import { navigateTo } from '../router.js';
import { HTTPError } from '../api/index.js';

async function handleLoginResponse(response) {
  if (response.status === 'success') {
    if (response.requires_2fa) {
      navigateTo('/login-2fa');
    } else {
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      setTimeout(async () => {
        window.isAuthenticated = true;
        await handleNavbar();
        navigateTo('/home');
      }, 500);
    }
  } else {
    showStatusMessage(response.message, 'error');
  }
}

async function submitLogin(form) {
  const validateBtn = document.querySelector('#validate-btn');
  validateBtn.disabled = true;
  validateBtn.textContent = 'Connexion...';
  const formData = new FormData(form);
  try {
    const response = await requestPost('accounts', 'submit_login', formData);
    console.debug('Réponse POST submit_login :', response);
    return response;
  } catch (error) {
    console.error('Erreur lors de la connexion :', error);
    showStatusMessage('Erreur lors de la connexion. Veuillez réessayer.', 'error');
    return null;
  } finally {
    validateBtn.disabled = false;
    validateBtn.textContent = 'Valider';
  }
}

async function initializeLoginForm() {
  try {
    const data = await requestGet('accounts', 'login');
    updateHtmlContent('#content', data.html);
    const form = document.querySelector('#login-form');
    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const response = await submitLogin(form);
        if (response) {
          await handleLoginResponse(response);
        }
      });
    }
  } catch (error) {
    if (error instanceof HTTPError && error.status === 403) {
      showStatusMessage('Vous êtes déjà connecté. Redirection...', 'error');
      navigateTo('/home');
      return;
    }
    console.error('Erreur dans initializeLoginForm :', error);
    showStatusMessage('Impossible de charger la vue de connexion. Veuillez réessayer.', 'error');
  }
}

export async function handleLogin() {
  try {
    await initializeLoginForm();
  } catch (error) {
    console.error('Erreur dans handleLogin :', error);
    showStatusMessage('Erreur lors de l\'initialisation de la connexion.', 'error');
  }
}
