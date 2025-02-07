// game/display.js
import { requestGet }  from '../api/index.js';
import { resetScrollPosition } from '../tools/index.js';


//[IMPROVE] Voir quoi afficher avec le get
export async function displayGame() {
    try {
        const response = await requestGet('game', 'game');
        document.querySelector('#home').innerHTML = response.html || response;
        resetScrollPosition();
    } catch (error) {
        console.log('Erreur chargement jeu:', error);
    }
}

export async function displayTournamentBracket(participantCount) {
    const url = participantCount === 4 ? 'bracket_4.html' : 'bracket_8.html';
    try {
        const response = await Api.get(url);
        document.querySelector('#home').innerHTML = response.html || response;
        resetScrollPosition();
    } catch (error) {
        console.log('Erreur chargement bracket:', error);
    }
}
