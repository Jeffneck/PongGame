import { navigateTo } from '/static/js/router.js';
import { requestGet, requestPost } from '/static/js/api/index.js';
import { updateHtmlContent, showStatusMessage } from '/static/js/tools/index.js';

// Gestionnaire principal pour activer la 2FA
export async function handleEnable2FA() {
    console.log('Activation de la 2FA...');
    try {
        await loadEnable2FAView(); // Charge la vue d'activation de la 2FA
    } catch (error) {
        console.error('Erreur dans handleEnable2FA:', error);
        showStatusMessage('Erreur lors de l\'activation de la 2FA.', 'error');
    }
}

// Fonction pour charger la vue d'activation de la 2FA
async function loadEnable2FAView() {
    try {
        const response = await requestGet('accounts', '2fa/enable');
        if (response.status === 'success' && response.html) {
            updateHtmlContent('#content', response.html); // Met à jour la vue

            // Attache l'événement de vérification
            attach2FAVerificationEvent();
        } else {
            throw new Error(response.message || 'Erreur lors du chargement de la vue 2FA.');
        }
    } catch (error) {
        console.error('Erreur lors du chargement de la vue 2FA:', error);
        showStatusMessage('Impossible de charger la vue d\'activation de la 2FA.', 'error');
        throw error;
    }
}

// Fonction pour gérer la soumission du formulaire de vérification 2FA
async function verification2FA(event) {
    event.preventDefault(); // Empêche le comportement par défaut

    console.log('Soumission du formulaire de vérification 2FA...');
    const form = event.target;
    const formData = new FormData(form);

    try {
        const response = await requestPost('accounts', '2fa/check', formData);
        if (response.status === 'success') {
            showStatusMessage('2FA activée avec succès.', 'success');
            navigateTo('/account');
        } else {
            throw new Error(response.message || 'Code 2FA incorrect.');
        }
    } catch (error) {
        console.error('Erreur lors de la vérification 2FA:', error);
        showStatusMessage('Une erreur est survenue lors de la vérification 2FA.', 'error');
        throw error;
    }
}

// Fonction pour attacher l'événement de vérification
function attach2FAVerificationEvent() {
    const verifyForm = document.querySelector('#verify-2fa-form');
    if (verifyForm) {
        verifyForm.addEventListener('submit', async (event) => {
            try {
                await verification2FA(event); // Gère la soumission du formulaire
            } catch (error) {
                console.error('Erreur lors de la vérification 2FA dans attach2FAVerificationEvent:', error);
                showStatusMessage('Une erreur est survenue lors de la vérification 2FA.', 'error');
            }
        });
        console.log('Événement de vérification 2FA attaché.');
    } else {
        console.error('Formulaire de vérification 2FA introuvable.');
        showStatusMessage('Formulaire de vérification introuvable. Veuillez réessayer.', 'error');
    }
}
