import { requestGet} from "../api/index.js";
import { updateHtmlContent } from "../tools/index.js";
import { showStatusMessage } from "../tools/index.js";


export async function showResults(gameId) {
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