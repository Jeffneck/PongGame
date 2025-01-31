import { requestPost } from '../api/api.js';
import { handleDeleteAccount } from '../auth/index.js';
import { navigateTo } from '../router.js';

async function handleLanguageChange(language) {
    const formData = new FormData();
    console.log(language);
    formData.append('language', language); // Ajoute la paire clé-valeur "language=fr"
    const data = await  requestPost('accounts', 'set_language', formData);
    if (data.status === 'success') {
        location.reload(); // Recharge la page pour appliquer la langue
    }
}

export function attachProfileEvents() {
    // Bouton Activer 2FA
    const enable2FABtn = document.querySelector('#enable-2fa-btn');
    if (enable2FABtn && !enable2FABtn.dataset.bound) {
        enable2FABtn.addEventListener('click', () => {
            navigateTo('/enable-2fa');
        });
        enable2FABtn.dataset.bound = true;
    }

    // Bouton Désactiver 2FA
    const disable2FABtn = document.querySelector('#disable-2fa-btn');
    if (disable2FABtn && !disable2FABtn.dataset.bound) {
        disable2FABtn.addEventListener('click', () => {
            navigateTo('/disable-2fa');
        });
        disable2FABtn.dataset.bound = true;
    }

    // Bouton Supprimer le compte
    const deleteAccountBtn = document.querySelector('#delete-account-btn');
    if (deleteAccountBtn && !deleteAccountBtn.dataset.bound) {
        deleteAccountBtn.addEventListener('click', handleDeleteAccount);
        deleteAccountBtn.dataset.bound = true;
    }

    // Sélectionne tous les boutons de langue
    const languageButtons = document.querySelectorAll('button[data-lang]');
    // Ajoute un gestionnaire d'événements à chaque bouton
    languageButtons.forEach(button => {
        if (!button.dataset.bound) { // Empêche les doublons
            button.addEventListener('click', event => {
                event.preventDefault(); // Empêche le comportement par défaut (soumission du formulaire)
                handleLanguageChange(button.dataset.lang); // Récupère la valeur
            });
        button.dataset.bound = true;
        }
    });
}
