"use strict";
import { requestGet, requestPost } from '/static/js/api/index.js';
import { updateHtmlContent, showStatusMessage } from '/static/js/tools/index.js';
import { navigateTo } from '/static/js/router.js';

async function loadDisable2FAView() {
  try {
    console.debug('Chargement de la vue de désactivation de la 2FA...');
    const modal = document.getElementById('delete-account-modal');
    if (!modal) {
      throw new Error('Modale de désactivation introuvable.');
    }
    modal.style.display = 'flex';
    return true;
  } catch (error) {
    console.error('Erreur dans loadDisable2FAView:', error);
    showStatusMessage('Impossible de charger la vue de désactivation.', 'error');
    throw error;
  }
}

function attachDisable2FAEvent() {
  try {
    const modal = document.getElementById('delete-account-modal');
    const closeBtn = modal.querySelector('.close-btn');
    const deleteAccountForm = document.getElementById('delete-account-form');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
      });
    }
    window.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.style.display = 'none';
      }
    });
    if (deleteAccountForm) {
      deleteAccountForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        await submitDisable2FA(deleteAccountForm);
      });
    } else {
      throw new Error("Formulaire de désactivation introuvable.");
    }
  } catch (error) {
    console.error('Erreur dans attachDisable2FAEvent:', error);
    showStatusMessage('Erreur lors de l\'attachement des événements.', 'error');
    throw error;
  }
}

async function submitDisable2FA(form) {
  const formData = new FormData(form);
  console.debug('Soumission du formulaire de désactivation de la 2FA...');
  try {
    const response = await requestPost('accounts', '2fa/disable', formData);
    if (response.status === 'success') {
      showStatusMessage('La 2FA a été désactivée avec succès.', 'success');
      setTimeout(() => {
        navigateTo('/account');
      }, 2000);
    } else {
      throw new Error(response.message || 'Échec de la désactivation de la 2FA.');
    }
  } catch (error) {
    console.error('Erreur dans submitDisable2FA:', error);
    showStatusMessage('Erreur lors de la désactivation de la 2FA.', 'error');
    throw error;
  }
}

export async function handleDisable2FA() {
  try {
    console.debug('Désactivation de la 2FA...');
    await loadDisable2FAView();
    await attachDisable2FAEvent();
  } catch (error) {
    console.error('Erreur dans handleDisable2FA:', error);
    showStatusMessage('Erreur lors de la désactivation.', 'error');
  }
}
