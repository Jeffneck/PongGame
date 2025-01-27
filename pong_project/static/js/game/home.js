import { updateHtmlContent } from '../tools/index.js';
import { requestGet } from '../api/index.js';
import { navigateTo } from '../router.js';
import { showStatusMessage } from '../tools/index.js';

/**
 * Initialise la vue de la page d'accueil du jeu.
 * Redirige vers la page de jeu si l'utilisateur est authentifié.
 */
export async function initializeGameHomeView() {
    console.log('initializeGameHomeView démarré');

    try {
        const data = await requestGet('game', 'home');

        if (data && data.html) {
            updateHtmlContent('#content', data.html);
        } else {
            showStatusMessage('Les données HTML de la page d\'accueil sont manquantes ou invalides.', 'error');
        }
    } catch (error) {
        showStatusMessage('Erreur lors du chargement de la page d\'accueil du jeu.', 'error');
        console.error('Erreur lors de la requête API initializeGameHomeView :', error);
        return;
    }

    const playBtn = document.querySelector('#play-btn-home');
    if (!playBtn) {
        showStatusMessage('Le bouton "Jouer" est introuvable dans la vue actuelle.', 'error');
        return;
    }
    
    if (!playBtn.dataset.bound) {
        playBtn.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('Bouton "Jouer" cliqué. Redirection vers /game-options.');
            navigateTo('/game-options');
        });
        playBtn.dataset.bound = true; // Empêche de lier plusieurs fois l'événement
    }

    console.log('initializeGameHomeView terminé.');
}