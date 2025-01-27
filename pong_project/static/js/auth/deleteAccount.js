import { requestPost } from '../api/index.js';
import { clearSessionAndUI, showStatusMessage} from '../tools/index.js';

// Charge et affiche la modale de suppression
async function loadDeleteAccountView() {
    console.log('Chargement de la vue de suppression...');
    try {
        const modal = document.getElementById('delete-account-modal');
        if (!modal) {
            throw new Error('La modale de suppression du compte est introuvable.');
        }
        modal.style.display = 'flex'; // Affiche la modale
    } catch (error) {
        console.error('Erreur dans loadDeleteAccountView:', error);
        showStatusMessage('Impossible de charger la vue de suppression. Veuillez réessayer.', 'error');
        throw error;
    }
}

// Attache les événements nécessaires à la modale de suppression
async function attachDeleteAccountEvents() {
    console.log('Attachement des événements pour la suppression du compte...');
    try {
        const modal = document.getElementById('delete-account-modal');
        const closeBtn = modal.querySelector('.close-btn');
        const deleteAccountForm = document.getElementById('delete-account-form');

        // Fermer la modale via le bouton de fermeture
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                modal.style.display = 'none';
            });
        }

        // Fermer la modale en cliquant en dehors de son contenu
        window.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });

        // Gestion de la soumission du formulaire de suppression
        if (deleteAccountForm) {
            deleteAccountForm.addEventListener('submit', async (event) => {
                event.preventDefault(); // Empêche le comportement par défaut
                await submitDeleteAccount(deleteAccountForm);
            });
        }
    } catch (error) {
        console.error('Erreur dans attachDeleteAccountEvents:', error);
        showStatusMessage('Erreur lors de l\'attachement des événements de suppression.', 'error');
        throw error;
    }
}

// Soumet la requête de suppression de compte
async function submitDeleteAccount(form) {
    const formData = new FormData(form);
    console.log('Soumission du formulaire de suppression de compte...');

    try {
        const response = await requestPost('accounts', 'profile/delete_account', formData);

        if (response.status !== 'success') {
            console.error('Erreur serveur :', response.message);
            showStatusMessage(response.message || 'Erreur lors de la suppression du compte.', 'error');
            return;
        }

        showStatusMessage('Votre compte a été supprimé avec succès.', 'success');

        setTimeout(() => {
            clearSessionAndUI();
        }, 5000);
    } catch (error) {
        console.error('Erreur lors de la soumission de la suppression du compte :', error);
        showStatusMessage('Une erreur est survenue. Veuillez réessayer.', 'error');
    }
}

// Gestionnaire principal pour la suppression de compte
export async function handleDeleteAccount() {
    console.log('Suppression du compte...');
    try {
        await loadDeleteAccountView(); // Charge et affiche la modale de suppression
        await attachDeleteAccountEvents();
    } catch (error) {
        console.error('Erreur dans handleDeleteAccount:', error);
        showStatusMessage('Erreur lors de la tentative de suppression du compte.', 'error');
    }
}
