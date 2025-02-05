import { requestGet, requestPost } from "../api/index.js";
import { updateHtmlContent } from "../tools/index.js";
import { showStatusMessage } from "../tools/index.js";
// import { isTouchDevice } from "../tools/index.js";
// import { initializeGameControls } from "./controls.js";
import { launchLiveGameWithOptions } from "./live_game.js";
// import { HTTPError } from "../api/index.js";

export async function handleLocalGame(parametersForm) {
    // Poster vers ton endpoint
	try {
		const response = await requestPost('game', 'create_local_game', parametersForm);
		if (response.status === 'success')
		{
			showStatusMessage(`Partie créée avec succès : ID = ${response.game_id}`, 'success');
			updateHtmlContent('#content', response.html);
			const gameId = response.game_id;
			await launchLiveGameWithOptions(gameId, 'both', `start_local_game/${gameId}`);
			// Attendre quelques secondes (par exemple, 3 secondes)
			await showWinner(gameId)
			//IMPROVE afficher une page présentant le winner et looser une fois la game terminee
		}
		else{
			// alert(response.message);
			showStatusMessage(response.message, 'error');

		}
	} catch (err) {
		console.error('Error local game', err);
		showStatusMessage('Error local game', 'error');
	}
}

async function showWinner(gameId) {
	try {
		const response = await requestGet('game', `game_results/${gameId}` );
		if (response.status === 'success')
		{
			showStatusMessage(`Partie terminée ! \nwinner : ${response.winner}  looser : ${response.looser}\n${response.score_left} - ${response.score_right}`, 'success');
			updateHtmlContent('#content', response.html);
			
			// IMPROVE : adapter l' ui de en modifiant le dom pour afficher winner
		}
		else{
			// alert(response.message);
			showStatusMessage(response.message, 'error');
		}
	} catch (err) {
		// console.error('Erreur lors de la création de la partie :', err);
		showStatusMessage('Impossible d\'obtenir les resultats', 'error');
	}
}