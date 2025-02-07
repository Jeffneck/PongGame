// loadnavbar.js

import { toggleBurgerMenu } from './toggleBurgerMenu.js';
import { requestGet } from '../api/index.js';
import { updateHtmlContent, showStatusMessage } from '../tools/index.js';
import { initBurgerMenuDelegation } from './delegation.js'; // Notre module de délégation
import { eventsHandlerBurgerMenu } from '../burgerMenu/index.js';
import { navigateTo } from '../router.js'; // Pour naviguer

/**
 * Initialise le burger menu : attache l'événement sur le bouton de toggle.
 */
async function initializeBurgerMenu(flag) {
    const burgerToggle = document.querySelector('#burger-menu-toggle');
    if (burgerToggle && !burgerToggle.dataset.bound) {
        burgerToggle.addEventListener('click', () => toggleBurgerMenu(flag));
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
        navigateTo('/');
    }
}

/**
 * Charge et affiche la navbar, puis initialise le burger menu.
 */
async function loadNavbar() {
    console.log('Début de loadNavbar');
    try {
        // Récupère les données de la navbar
        const data = await requestGet('core', 'navbar');

        if (data && data.html) {
            // Met à jour le contenu HTML de la navbar
            updateHtmlContent('#navbar', data.html);
            console.log('Contenu de la navbar mis à jour.');

            // Attache l'événement au bouton "home"
            const homeButton = document.querySelector('#home-btn');
            if (homeButton && !homeButton.dataset.bound) {
                homeButton.addEventListener('click', () => handleHomeButtonClick(data.is_authenticated));
                homeButton.dataset.bound = true;
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
 * Rafraîchit le contenu du burger menu.
 */
export async function refreshBurgerMenu() {
    try {
        let menu = document.getElementById('burger-menu');
        let overlay = document.getElementById('overlay');

        if (!menu || !overlay) return;

        const data = await requestGet('accounts', 'burgerMenu');
        if (data.status === 'success') {
            // Mise à jour du contenu du burger menu selon son état d'affichage
            if (menu.style.display === 'block') {
                updateHtmlContent('#burger-menu-container', data.html);
                menu = document.getElementById('burger-menu');
                overlay = document.getElementById('overlay');
                menu.style.display = 'block';
                overlay.style.display = 'block';
            } else {
                updateHtmlContent('#burger-menu-container', data.html);
                menu = document.getElementById('burger-menu');
                overlay = document.getElementById('overlay');
                menu.style.display = 'none';
                overlay.style.display = 'none';
            }
            // Réinitialise le burger menu (pour le bouton de toggle, etc.)
            await initializeBurgerMenu('refresh btn');
            eventsHandlerBurgerMenu();

            console.log('Burger menu mis à jour avec succès.');
        } else {
            console.warn('Burger menu non mis à jour, statut:', data.status);
        }
    } catch (error) {
        console.error('Erreur lors du rafraîchissement du burger menu:', error);
    }
}

/**
 * Gère le chargement de la navbar et du burger menu.
 */
export async function handleNavbar() {
    console.log('Chargement de la navbar...');
    try {
        const is_authenticated = await loadNavbar();

        if (is_authenticated) {
            await initializeBurgerMenu(null);
            // Initialise la délégation d'événements pour le burger menu
            initBurgerMenuDelegation();
            eventsHandlerBurgerMenu();
            console.log('Navbar et burger menu chargés avec succès.');
            // Rafraîchissement périodique si l'utilisateur est authentifié
            setInterval(refreshBurgerMenu, 10000);
        } else {
            console.log('Utilisateur non authentifié ou erreur de chargement.');
        }
    } catch (error) {
        console.error('Erreur lors du chargement de la navbar dans handleNavbar:', error);
        showStatusMessage('Erreur lors du chargement de la barre de navigation. Veuillez réessayer.', 'error');
    }
}
