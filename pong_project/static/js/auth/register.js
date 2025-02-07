"use strict";
import { requestPost, requestGet } from '../api/index.js';
import { updateHtmlContent, showStatusMessage } from '../tools/index.js';
import { navigateTo } from '../router.js';
import { HTTPError } from '../api/index.js';

function handleRegisterResponse(response) {
  if (response.status === 'success') {
    showStatusMessage(response.message, 'success');
    navigateTo('/login');
  } else {
    showStatusMessage(response.message, 'error');
  }
}

async function submitRegistration(form) {
  const submitBtn = document.querySelector('#submit-btn');
  submitBtn.disabled = true;
  submitBtn.textContent = 'Inscription en cours...';
  const formData = new FormData(form);
  try {
    const response = await requestPost('accounts', 'submit_register', formData);
    console.debug('Réponse POST submit_register :', response);
    handleRegisterResponse(response);
  } catch (error) {
    console.error('Erreur lors de l\'inscription :', error);
    showStatusMessage('Erreur lors de l\'inscription. Veuillez réessayer.', 'error');
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'S\'inscrire';
  }
}

export async function initializeRegisterView() {
  try {
    const data = await requestGet('accounts', 'register');
    updateHtmlContent('#content', data.html);
    const form = document.querySelector('#register-form');
    if (form) {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        submitRegistration(form);
      });
    }
  } catch (error) {
    if (error instanceof HTTPError && error.status === 403) {
      showStatusMessage('Vous êtes déjà connecté. Redirection...', 'error');
      navigateTo('/home');
      return;
    }
    console.error('Erreur dans initializeRegisterView :', error);
    showStatusMessage('Impossible de charger la vue d\'inscription. Veuillez réessayer.', 'error');
  }
}
