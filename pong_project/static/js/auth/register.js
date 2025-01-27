// auth/register.js
import { requestPost, requestGet } from '../api/index.js';
import { updateHtmlContent, showStatusMessage } from '../tools/index.js';
import { navigateTo } from '../router.js'; // Importer la fonction pour naviguer

function handleRegisterResponse(response) {
    if (response.status === 'success') {
        showStatusMessage(response.message, 'success');
        navigateTo('/login');
    } else if (response.errors) {
        const errorMessages = Object.keys(response.errors)
            .map(field => response.errors[field].join('<br>'))
            .join('<br>');
        showStatusMessage(errorMessages, 'error');
    }
}

async function submitRegistration(form) {
    const submitBtn = document.querySelector('#submit-btn');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Inscription en cours...';

    const formData = new FormData(form);

    try {
        const response = await requestPost('accounts', 'submit_register', formData);
        console.log('Réponse de la requête POST submit_register :', response);
        handleRegisterResponse(response);
        
    } catch (error) {
        console.error('Erreur lors de l\'inscription :', error);
        showStatusMessage('Une erreur est survenue lors de l\'inscription. Veuillez réessayer.', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'S\'inscrire';
    }
}

// MAIN FUNCTION
export async function initializeRegisterView() {
    console.log('initializeRegisterView');

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
        console.error('Erreur lors de la requête API initializeRegisterView :', error);
        showStatusMessage('Impossible de charger la vue d\'inscription. Veuillez réessayer.', 'error');
    }
}
