"use strict";
import { requestPost } from '../api/api.js';
import { handleDeleteAccount } from '../auth/index.js';
import { navigateTo } from '../router.js';

async function handleLanguageChange(language) {
  try {
    const formData = new FormData();
    console.debug("Changement de langue vers :", language);
    formData.append('language', language);
    const data = await requestPost('accounts', 'set_language', formData);
    if (data.status === 'success') {
      location.reload(); // Recharge la page pour appliquer la langue
    } else {
      console.error("Erreur lors du changement de langue :", data.message);
    }
  } catch (error) {
    console.error("Erreur handleLanguageChange :", error);
  }
}

export function attachProfileEvents() {
  // Bouton Activer 2FA
  const enable2FABtn = document.querySelector('#enable-2fa-btn');
  if (enable2FABtn && !enable2FABtn.dataset.bound) {
    enable2FABtn.addEventListener('click', () => navigateTo('/enable-2fa'));
    enable2FABtn.dataset.bound = true;
  }

  // Bouton Désactiver 2FA
  const disable2FABtn = document.querySelector('#disable-2fa-btn');
  if (disable2FABtn && !disable2FABtn.dataset.bound) {
    disable2FABtn.addEventListener('click', () => navigateTo('/disable-2fa'));
    disable2FABtn.dataset.bound = true;
  }

  // Bouton Supprimer le compte
  const deleteAccountBtn = document.querySelector('#delete-account-btn');
  if (deleteAccountBtn && !deleteAccountBtn.dataset.bound) {
    deleteAccountBtn.addEventListener('click', handleDeleteAccount);
    deleteAccountBtn.dataset.bound = true;
  }

  // Boutons de langue
  const languageButtons = document.querySelectorAll('button[data-lang]');
  languageButtons.forEach((button) => {
    if (!button.dataset.bound) {
      button.addEventListener('click', (event) => {
        event.preventDefault();
        handleLanguageChange(button.dataset.lang);
      });
      button.dataset.bound = true;
    }
  });
}
