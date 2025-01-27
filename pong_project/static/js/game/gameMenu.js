import { requestGet, requestPost } from '../api/index.js'; 
import { updateHtmlContent } from '../tools/index.js'; 
import { handleInviteGame } from './handleInvitationGame.js'; // Suppose qu'on gère l'invitation en ligne ici

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
        console.log(`test:`, test);

        console.log(`inviteGameButton:`, inviteGameButton);

        // Définir un comportement différent selon le bouton
        if (startGameButton && section === 'local') {
            startGameButton.addEventListener('click', async () => {
                const formData = new FormData();
                formData.append('game_type', section);

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
                formData.append('ball_speed', ballSpeedElement.value);
                formData.append('paddle_size', paddleSizeElement.value);
                formData.append('bonus_enabled', bonusCheckbox?.checked ?? false);
                formData.append('obstacles_enabled', obstacleCheckbox?.checked ?? false);

                // Poster vers ton endpoint
                try {
                    const response = await requestPost('game', 'create_local_game', formData);
                    alert(`Partie créée avec succès : ID = ${response.game_id}`);
                } catch (err) {
                    console.error('Erreur lors de la création de la partie :', err);
                    alert('Impossible de créer la partie.');
                }
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
                        racket_size: paddleSizeElement.value,
                        bonus_malus_activation: bonusCheckbox?.checked ?? false,
                        bumpers_activation: obstacleCheckbox?.checked ?? false,
                    };
                    console.log('Paramètres de la partie online:', onlineParams);

                    // Maintenant on va charger la page "invite_game.html"
                    // et injecter le HTML dans #content (ou autre conteneur).
                    await handleInviteGame(onlineParams);

                } catch (err) {
                    console.error('Erreur lors de la phase d\'invitation :', err);
                    alert('Impossible d\'inviter un ami.');
                }
            });
        }

        if (inviteTournamentButton) {
            inviteTournamentButton.addEventListener('click', async () => {
                const formData = new FormData();
                formData.append('game_type', 'tournament');
                formData.append('tournament_name', document.getElementById('tournamentName').value); // Exemple pour un champ tournoi

                try {
                    const response = await requestPost('tournament/create', formData);
                    alert(`Tournoi créé avec succès : ID = ${response.tournament_id}`);
                } catch (err) {
                    console.error('Erreur lors de la création du tournoi :', err);
                    alert('Impossible de créer le tournoi.');
                }
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
