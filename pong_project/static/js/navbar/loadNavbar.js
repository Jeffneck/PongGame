import { toggleBurgerMenu } from './toggleBurgerMenu.js';
import { requestGet } from '../api/index.js';
import { updateHtmlContent, showStatusMessage } from '../tools/index.js';
import { eventsHandlerBurgerMenu } from '../burgerMenu/index.js';
import { navigateTo } from '../router.js'; // Importer la fonction pour naviguer

/**
 * Initialise le burger menu : attache les événements et configure le rechargement périodique.
 */
async function initializeBurgerMenu() {
    const burgerToggle = document.querySelector('#burger-menu-toggle');
    if (burgerToggle && !burgerToggle.dataset.bound) {
        burgerToggle.addEventListener('click', toggleBurgerMenu);
        burgerToggle.dataset.bound = true; // Marque comme attaché
        console.log('Événements du burger menu initialisés.');
    }
}


function handleHomeButtonClick(isAuthenticated) {
    if (isAuthenticated) {
        // Redirige vers la page de jeu
        navigateTo('/home');
    } else {
        // Redirige vers la page de connexion
        navigateTo('/login');
    }
}

/**
 * Charge et affiche la navbar, puis initialise le burger menu.
 */
async function loadNavbar() {
    console.log('Début de loadNavbar');
    try {
        // Faire une requête GET pour obtenir les données de la navbar
        const data = await requestGet('core', 'navbar');

        // Vérifie si les données HTML existent
        if (data && data.html) {
            // Met à jour le contenu HTML de la navbar
            updateHtmlContent('#navbar', data.html);
            console.log('Contenu de la navbar mis à jour.');

            // Attache un gestionnaire d'événements au bouton "PONGAME"
            const homeButton = document.querySelector('#home-btn');
            if (homeButton && !homeButton.dataset.bound) {
                homeButton.addEventListener('click', () => handleHomeButtonClick(data.is_authenticated));
                homeButton.dataset.bound = true; // Évite d'attacher plusieurs fois
            }

            return data.is_authenticated;
        } else {
            console.error('Les données HTML de la navbar sont manquantes.');
            showStatusMessage('Impossible de charger la barre de navigation.', 'error');
            return false;
        }
    } catch (error) {
        console.error('Erreur lors du chargement de la navbar:', error);
        showStatusMessage('Une erreur est survenue lors du chargement de la barre de navigation.', 'error');
        throw error;
    } finally {
        console.log('Fin de loadNavbar');
    }
}

/**
 * Gestionnaire pour charger et afficher la navbar.
 * Gère les erreurs et affiche des messages appropriés en cas de problème.
 */

export async function handleNavbar() {
    console.log('Chargement de la navbar...');
    try {
        const is_authenticated = await loadNavbar(); // Charge le contenu de la navbar et initialise les événements

        if (is_authenticated) {
            await initializeBurgerMenu();
            eventsHandlerBurgerMenu();
            console.log('Navbar et burger menu chargés avec succès.');
        } else {
            console.log('Utilisateur non authentifié ou erreur de chargement.');
        }
    } catch (error) {
        console.error('Erreur lors du chargement de la navbar dans handleNavbar:', error);
        showStatusMessage('Erreur lors du chargement de la barre de navigation. Veuillez réessayer.', 'error');
    }
}
