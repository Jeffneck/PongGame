import { requestPost } from '../api/index.js';
import { navigateTo } from '../router.js';
import { showStatusMessage } from '../tools/displayInfo.js';
import { attachProfileEvents } from './events.js';
import { handleNavbar } from '../navbar/index.js';
import { handleLogout } from '../auth/index.js';

// Fonction pour gérer la soumission des formulaires
async function handleFormSubmit(form, app, view, successMessage, successSelector) {
    const formData = new FormData(form);
    try {
        const response = await requestPost(app, view, formData);
        if (response.status === 'success') {
            const successElem = document.querySelector(successSelector);
            if (successElem) {
                successElem.textContent = successMessage;
                successElem.style.display = 'block';
                setTimeout(() => successElem.style.display = 'none', 3000);
            }
            form.reset();
            if (successSelector === '#change-avatar-success') {
                await handleNavbar(); 
            }
            else if (successSelector === '#change-username-success') {
                await handleLogout();
            }
            navigateTo('/account')
           
        } else {
            showStatusMessage(response.message, "error");
        }
    } catch (error) {
        console.error(`Erreur lors de la requête vers ${app}/${view}:`, error);
        showStatusMessage(response.message, "error");
    }
}

// Initialise les gestionnaires pour les formulaires
export function initializeaccountsManagementFormHandlers() {
    document.querySelectorAll('form').forEach((form) => {
        if (!form.hasAttribute('data-handled')) {
            form.addEventListener('submit', async function(e) {
                e.preventDefault();

                switch (form.id) {
                    case 'change-username-form':
                        await handleFormSubmit(form, 'accounts', 'profile/update', 'Pseudo mis à jour!', '#change-username-success');
                        break;
                    case 'change-password-form':
                        await handleFormSubmit(form, 'accounts', 'profile/change_password', 'Mot de passe mis à jour!', '#change-password-success');
                        break;
                    case 'change-avatar-form':
                        await handleFormSubmit(form, 'accounts', 'profile/update_avatar', 'Avatar mis à jour!', '#change-avatar-success');
                        break;
                    case 'delete-account-form':
                        break;
                    default:
                        console.warn('Formulaire non reconnu:', form.id);
                }
            });
            form.setAttribute('data-handled', 'true');
        }
    });

    // Attache les événements spécifiques aux boutons du profil
    attachProfileEvents();
}
    