import { requestGet, requestPost } from '../api/index.js';
import { handleNavbar } from '../navbar/index.js';
import { updateHtmlContent, showStatusMessage } from '../tools/index.js';
import { navigateTo } from '../router.js'; // Importer la fonction pour naviguer


async function handleLoginResponse(response) {
    console.log('handleLoginResponse');
    if (response.status === 'success') {
        if (response.requires_2fa) {
            navigateTo('/login-2fa');
        } else {
            console.log("Access token = ", response.access_token);
            localStorage.setItem('access_token', response.access_token);
            localStorage.setItem('refresh_token', response.refresh_token);

            setTimeout(async () => {
                window.isAuthenticated = true;
                await handleNavbar();
                navigateTo('/home');
            }, 500);
        }
    } else {
        const message = response.errors?.join('<br>') || response.message || 'Erreur inconnue.';
        showStatusMessage(message, 'error');
    }
}

async function submitLogin(form) {
    console.log('submitLogin');
    const validateBtn = document.querySelector('#validate-btn');
    validateBtn.disabled = true;
    validateBtn.textContent = 'Connexion...';

    const formData = new FormData(form);

    try {
        const response = await requestPost('accounts', 'submit_login', formData);
        console.log('Réponse de la requête POST submit_login :', response);
        return response;
    } catch (error) {
        console.error('Erreur lors de la connexion :', error);
        showStatusMessage('Une erreur est survenue. Veuillez réessayer.', 'error');
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
                console.log('Soumission du formulaire de connexion');
                const response = await submitLogin(form);
                if (response) {
                    await handleLoginResponse(response);
                }
            });
        }
    } catch (error) {
        console.error('Erreur lors de l\'initialisation du formulaire :', error);
        showStatusMessage('Impossible de charger la vue de connexion. Veuillez réessayer.', 'error');
    }
}

export async function handleLogin() {
    try {
        console.log('Initialisation de la vue de connexion');
        await initializeLoginForm();
        console.log('Vue de connexion initialisée avec succès');
    } catch (error) {
        console.error('Erreur dans handleLogin :', error);
        showStatusMessage('Erreur lors de l\'initialisation de la connexion.', 'error');
    }
}
