"use strict";
import { requestPost } from '../api/index.js';
import { clearSessionAndUI, showStatusMessage } from '../tools/index.js';

async function loadDeleteAccountView() {
  try {
    console.debug('Chargement de la vue de suppression...');
    const modal = document.getElementById('delete-account-modal');
    if (!modal) {
      throw new Error('La modale de suppression est introuvable.');
    }
    modal.style.display = 'flex';
    return true;
  } catch (error) {
    console.error('Erreur dans loadDeleteAccountView:', error);
    showStatusMessage('Impossible de charger la vue de suppression.', 'error');
    throw error;
  }
}

async function attachDeleteAccountEvents() {
  try {
    const modal = document.getElementById('delete-account-modal');
    const closeBtn = modal.querySelector('.close-btn');
    const deleteAccountForm = document.getElementById('delete-account-form');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => { modal.style.display = 'none'; });
    }
    window.addEventListener('click', (e) => { if (e.target === modal) modal.style.display = 'none'; });
    if (deleteAccountForm) {
      deleteAccountForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        await submitDeleteAccount(deleteAccountForm);
      });
    } else {
      throw new Error('Formulaire de suppression introuvable.');
    }
  } catch (error) {
    console.error('Erreur dans attachDeleteAccountEvents:', error);
    showStatusMessage('Erreur lors de l\'attachement des événements de suppression.', 'error');
    throw error;
  }
}

async function submitDeleteAccount(form) {
  const formData = new FormData(form);
  try {
    const response = await requestPost('accounts', 'profile/delete_account', formData);
    if (response.status !== 'success') {
      throw new Error(response.message || 'Erreur lors de la suppression du compte.');
    }
    showStatusMessage('Votre compte a été supprimé avec succès.', 'success');
    setTimeout(() => { clearSessionAndUI(); }, 1500);
  } catch (error) {
    console.error('Erreur dans submitDeleteAccount:', error);
    showStatusMessage('Une erreur est survenue lors de la suppression.', 'error');
  }
}

export async function handleDeleteAccount() {
  try {
    await loadDeleteAccountView();
    await attachDeleteAccountEvents();
  } catch (error) {
    console.error('Erreur dans handleDeleteAccount:', error);
    showStatusMessage('Erreur lors de la suppression du compte.', 'error');
  }
}
