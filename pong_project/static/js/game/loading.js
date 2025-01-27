// game/loading.js
import { requestGet }  from '../api/index.js';


// [IMPROVE] verifeir import
//import Animations from '../modules/animations.js';
import { isTouchDevice } from '../tools/utility.js';
import { updateHtmlContent } from '../tools/domHandler.js';
import { initializeGameControls } from './controls.js';
import { displayGame, displayTournamentBracket } from './display.js';

export async function startLoading(participantCount) {
    try {
        const response = await requestGet('game', 'loading');
        updateHtmlContent('#content', response.html);
        //Animations.animateLoadingText();
        if (isTouchDevice()) {
            initializeGameControls('touch');
        } else {
            initializeGameControls('keyboard');
        }

        setTimeout(() => {
            if (participantCount === 1) {
                displayGame();
            } else {
                displayTournamentBracket(participantCount);
            }
        }, 20000);
    } catch (error) {
        console.log('Erreur chargement page loading:', error);
    }
}
