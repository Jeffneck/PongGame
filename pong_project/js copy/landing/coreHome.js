import { requestGet } from '../api/index.js';
import { HTTPError } from '../api/index.js';
import { updateHtmlContent, showStatusMessage } from '../tools/index.js';
import { navigateTo } from '../router.js'; // Importer la fonction pour naviguer

function attachNavigationEvents() {
    const loginBtn = document.querySelector('#login-btn');
    if (loginBtn) {
        loginBtn.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('login clicked');
            navigateTo('/login'); // Utiliser Navigo pour naviguer
        });
    }

    const registerBtn = document.querySelector('#register-btn');
    if (registerBtn) {
        registerBtn.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('register clicked');
            navigateTo('/register'); // Utiliser Navigo pour naviguer
        });
    }
}

export async function initializeHomeView() {
    console.log('initializeHomeView');
    try {
        const data = await requestGet('core', 'home');

        if (data && data.html) {
            updateHtmlContent('#content', data.html);
        } else {
            console.error("Les données HTML de la page d'accueil sont manquantes.");
            showStatusMessage("Impossible de charger la page d'accueil.", 'error');
            return;
        }

    } catch (error) {
        if (error instanceof HTTPError) {
            if (error.status === 403) {
                console.error('Erreur 403 : Utilisateur déjà authentifié');
                showStatusMessage('Vous êtes déjà connecté. Redirection...', 'error');
                navigateTo('/home');
                return;
            }
        } else {
            console.error('Erreur non traitée lors de la récupération de core home :', error);
            showStatusMessage("Une erreur inattendue est survenue. Veuillez réessayer.", 'error');
        }
    }

    attachNavigationEvents();
    console.log('Fin de initializeHomeView');
}

