import { requestGet } from '../api/index.js';
import { updateHtmlContent } from '../tools/index.js'; 
import { handleInviteGame } from './invitation.js';


function attachGameMenuEvents() {
    console.log('Attachement des événements pour le menu du jeu.');

    // Bouton "Partie Locale"
    const localGameBtn = document.getElementById('local-game-btn');
    if (localGameBtn) {
        localGameBtn.addEventListener('click', () => {
            document.getElementById('game-modes').classList.remove('d-none');
            document.getElementById('customization-menu').classList.add('d-none');
        });
    }

    const inviteGameButton = document.querySelector('#invite-game-btn');
    if (inviteGameButton && !inviteGameButton.dataset.bound) {
        inviteGameButton.addEventListener('click', async (e) => {
            e.preventDefault();
            await handleInviteGame(); // Fonction à définir pour gérer l'invitation
        });
        inviteGameButton.dataset.bound = true; // Évite de lier plusieurs fois l'événement
    }

    // Bouton "Jeu Standard"
    const standardGameBtn = document.getElementById('standard-game-btn');
    if (standardGameBtn) {
        standardGameBtn.addEventListener('click', () => {
            alert("Lancement de la partie standard...");
            // Ajouter la logique AJAX pour lancer une partie standard
        });
    }

    // Bouton "Jeu Personnalisé"
    const customGameBtn = document.getElementById('custom-game-btn');
    if (customGameBtn) {
        customGameBtn.addEventListener('click', () => {
            document.getElementById('customization-menu').classList.remove('d-none');
        });
    }

    // Input pour la vitesse de la balle
    const ballSpeed = document.getElementById('ball_speed');
    if (ballSpeed) {
        ballSpeed.addEventListener('input', () => {
            document.getElementById('ballSpeedValue').innerText = ballSpeed.value;
            console.log("Vitesse de balle choisie :", ballSpeed.value);
        });
    }

    // // Select pour la taille de la raquette = affiche seulement un message de log (aucun comportement dynamique n'est declenché)
    // const racketSize = document.getElementById('racket_size');
    // if (racketSize) {
    //     racketSize.addEventListener('change', () => {
    //         console.log("Taille de la raquette choisie :", racketSize.value);
    //     });
    // }

    // Bouton pour lancer la partie personnalisée
    const startCustomGameBtn = document.querySelector('#customization-menu .btn-primary');
    if (startCustomGameBtn) {
        startCustomGameBtn.addEventListener('click', () => {
            alert("Lancement de la partie personnalisée avec les options choisies...");
            // Ajouter la logique AJAX pour lancer une partie personnalisée
        });
    }
}

export async function handleGameMenu() {
    console.log('Chargement du menu du jeu...');
    try {
        const response = await requestGet('game', 'menu');
        updateHtmlContent('#content', response.html);
        attachGameMenuEvents();
    } catch (error) {
        console.error('Erreur dans hangleGameMenu:', error);
        //displayErrorMessage('#content', 'Erreur lors du chargement du menu du jeu.');
    }
}


