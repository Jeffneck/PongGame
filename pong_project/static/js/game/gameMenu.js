import { requestGet, requestPost } from '../api/index.js'; 
import { updateHtmlContent } from '../tools/index.js'; 
// import { handleInviteGame } from './handleInvitationGame.js'; // Suppose qu'on gère l'invitation en ligne ici
// import { launchLiveGameWithOptions } from './live_game.js';
import { handleLocalGame } from './localGame.js'
import { createGameOnline } from './onlineGame.js'
import { handleTournament } from './tournament.js'

function attachGameMenuEvents() {
    const sections = ['local', 'online', 'tournament'];

    sections.forEach((section) => {
        // Bouton de sélection
        document.getElementById(`${section}-game-btn`)?.addEventListener('click', () => {
            sections.forEach((s) => {
                document.getElementById(`customization-${s}`).classList.add('d-none');
            });
            document.getElementById(`customization-${section}`).classList.remove('d-none');
        });

        // Bouton Voir Tuto
        document.getElementById(`tutorial-btn-${section}`)?.addEventListener('click', () => {
            const tutorialContent = document.getElementById(`tutorial-content-${section}`);
            tutorialContent.classList.toggle('collapse');
        });

        // Gestion de la vitesse de la balle
        document.getElementById(`ballSpeed${section.charAt(0).toUpperCase() + section.slice(1)}`)?.addEventListener('input', (event) => {
            console.log(`Vitesse de balle (${section}):`, event.target.value);
        });

        // Bouton principal (Lancer Partie, Inviter un ami, Lancer Tournoi)
        const startGameButton = document.getElementById(`start-game-btn-${section}`);
        const inviteGameButton = document.getElementById(`invite-game-btn-${section}`);
        const inviteTournamentButton = document.getElementById(`invite-tournament-btn-${section}`);
        const test = document.getElementById(`${section}-game-btn`); 

        // Définir un comportement différent selon le bouton
        if (startGameButton && section === 'local') {
            startGameButton.addEventListener('click', async () => {
                const parametersForm = new FormData();
                parametersForm.append('game_type', section);

                // Récupérer les éléments
                const ballSpeedElement = document.getElementById(`ballSpeed${section}`);
                const paddleSizeElement = document.getElementById(`paddleSizeSelect${section}`);
                const bonusCheckbox = document.getElementById(`bonus${section}`);
                const obstacleCheckbox = document.getElementById(`bonusObstacle${section}`);

                // Vérifier s’ils existent
                if (!ballSpeedElement || !paddleSizeElement) {
                    console.error(`Impossible de trouver les champs pour la section "${section}".`);
                    return;
                }
                    
                console.log(`Vitesse de balle (${section}):`, ballSpeedElement.value);
                console.log(`Taille de raquette (${section}):`, paddleSizeElement.value);
                console.log(`Bonus activé (${section}):`, bonusCheckbox?.checked);
                console.log(`Obstacles activés (${section}):`, obstacleCheckbox?.checked);
                // Lire les valeurs
                parametersForm.append('ball_speed', ballSpeedElement.value);
                parametersForm.append('paddle_size', paddleSizeElement.value);
                parametersForm.append('bonus_enabled', bonusCheckbox?.checked ?? false);
                parametersForm.append('obstacles_enabled', obstacleCheckbox?.checked ?? false);

                await handleLocalGame(parametersForm)
            });
        }

        if (startGameButton && section === 'online') {
            startGameButton.addEventListener('click', async () => {
                try {
                    // Récupère les éléments
                    const ballSpeedElement = document.getElementById(`ballSpeed${section}`);
                    const paddleSizeElement = document.getElementById(`paddleSizeSelect${section}`);
                    const bonusCheckbox = document.getElementById(`bonus${section}`);
                    const obstacleCheckbox = document.getElementById(`bonusObstacle${section}`);

                    if (!ballSpeedElement || !paddleSizeElement) {
                        console.error(`Impossible de trouver les champs pour la section "${section}".`);
                        return;
                    }
                    
                    // Stockage en mémoire JS
                    const onlineParams = {
                        ball_speed: ballSpeedElement.value,
                        paddle_size: paddleSizeElement.value,
                        bonus_enabled: bonusCheckbox?.checked ?? false,
                        obstacles_enabled: obstacleCheckbox?.checked ?? false,
                    };
                    console.log('Paramètres de la partie online:', onlineParams);

                    // Maintenant on va charger la page "invite_game.html"
                    // et injecter le HTML dans #content (ou autre conteneur).
                    await createGameOnline(onlineParams);

                } catch (err) {
                    console.error('Erreur lors de la phase d\'invitation :', err);
                    alert('Impossible d\'inviter un ami.');
                }
            });
        }

        if (startGameButton && section === 'tournament') {
            startGameButton.addEventListener('click', async () => {
                

                // Récupérer les éléments
                const ballSpeedElement = document.getElementById(`ballSpeed${section}`);
                const paddleSizeElement = document.getElementById(`paddleSizeSelect${section}`);
                const bonusCheckbox = document.getElementById(`bonus${section}`);
                const obstacleCheckbox = document.getElementById(`bonusObstacle${section}`);
                
                // Vérifier s’ils existent
                if (!ballSpeedElement || !paddleSizeElement) {
                    console.error(`Impossible de trouver les champs pour la section "${section}".`);
                    return;
                }

                 // Stockage en mémoire JS
                const onlineParams = {
                    ball_speed: ballSpeedElement.value,
                    paddle_size: paddleSizeElement.value,
                    bonus_enabled: bonusCheckbox?.checked ?? false,
                    obstacles_enabled: obstacleCheckbox?.checked ?? false,
                };

                await handleTournament(onlineParams);
                
                console.log(`Vitesse de balle (${section}):`, ballSpeedElement.value);
                console.log(`Taille de raquette (${section}):`, paddleSizeElement.value);
                console.log(`Bonus activé (${section}):`, bonusCheckbox?.checked);
                console.log(`Obstacles activés (${section}):`, obstacleCheckbox?.checked);
                

            });
        }
    });
}



export async function handleGameMenu() {
    console.log('Chargement du menu du jeu...');
    try {
        // 1) On va chercher le HTML du menu
        const response = await requestGet('game', 'menu');
        // 2) On injecte ce HTML dans la div #content
        updateHtmlContent('#content', response.html);
        // 3) On attache les événements
        attachGameMenuEvents();
    } catch (error) {
        console.error('Erreur dans handleGameMenu:', error);
    }
}
