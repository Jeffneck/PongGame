import { requestGet } from '../api/index.js';
import { updateHtmlContent, showStatusMessage } from '../tools/index.js';
import { navigateTo } from '../router.js'; // Importer la fonction pour naviguer

// Fonction principale qui récupère et affiche le profil utilisateur
async function viewUserProfile() {
    try {
        const response = await requestGet('accounts', 'userProfile');

        // Si la réponse est undefined, cela signifie que la redirection a déjà été déclenchée
        if (!response) {
            return false;
        }

        if (response.status === 'success' && response.html) {
            console.log('Profil utilisateur chargé avec succès.');
            updateHtmlContent('#content', response.html);
        } else {
            const message = response.message || 'Erreur lors du chargement du profil utilisateur.';
            console.error('Erreur :', message);
            showStatusMessage(message, 'error');
            throw new Error(message);
        }
    } catch (error) {
        console.error('Erreur réseau ou réponse lors du chargement du profil utilisateur:', error);
        showStatusMessage('Une erreur est survenue lors du chargement du profil utilisateur.', 'error');
        throw error; // Propagation de l'erreur pour gestion dans handleViewProfile
    }
}

// Fonction pour gérer les événements spécifiques au profil
async function initializeProfileEvents() {
    try {
        const gestionBtn = document.querySelector('#gestion-btn');
        if (!gestionBtn) {
            const message = 'Bouton de gestion de profil introuvable.';
            console.error(message);
            showStatusMessage(message, 'error');
            throw new Error(message);
        }

        gestionBtn.addEventListener('click', () => {
            console.log('Clic sur Gestion de Profil');
            navigateTo('/account'); 
        });

        console.log('Événements de profil initialisés.');
    } catch (error) {
        console.error('Erreur lors de l\'initialisation des événements de profil:', error);
        showStatusMessage('Une erreur est survenue lors de l\'initialisation des événements du profil.', 'error');
        throw error; // Relance l'erreur pour qu'elle soit gérée par handleViewProfile
    }
}

// Fonction pour gérer l'affichage du profil utilisateur
export async function handleViewProfile() {
    console.log('Chargement du profil utilisateur...');

    let profileLoaded;
    try {
        profileLoaded = await viewUserProfile(); // Appel de la fonction principale pour charger le profil
    } catch (error) {
        console.error('Erreur lors du chargement du profil utilisateur dans viewUserProfile:', error);
        showStatusMessage('Erreur lors du chargement du profil utilisateur.', 'error');
        return; // Arrête l'exécution si le chargement échoue
    }

    // Si le profil n'a pas été chargé (par exemple, à cause d'une redirection), on arrête ici.
    if (!profileLoaded) {
        return;
    }

    try {
        await initializeProfileEvents(); // Initialisation des événements spécifiques au profil
    } catch (error) {
        console.error('Erreur lors de l\'initialisation des événements dans initializeProfileEvents:', error);
        showStatusMessage('Erreur lors de l\'initialisation des événements du profil.', 'error');
    }
}

