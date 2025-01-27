import { requestGet } from "../api/index.js";
import { updateHtmlContent, displayErrorMessage } from "../tools/index.js";

async function loadSeclectTournament() {
    try {
        const response = await requestGet('game', 'select_tournament');
        if (response.status === 'success' && response.html) {
            updateHtmlContent('#content', response.html);
        }
        else {
            throw new Error(response.message || 'Erreur lors du chargement de la vue de selection du tournoi.');
        }
    } catch (error) {
        console.error('Erreur chargement selection du tournoi:', error);
        displayErrorMessage('#content', 'Erreur lors du chargement de la vue de selection du tournoi.');
    }
}

export async function handleSeclectTournament() {
    try {
        await loadSeclectTournament();
        // Si votre backend renvoie directement du HTML, utilisez-le tel quel.
        // Sinon, adaptez en fonction de ce qui est renvoyé.
    } catch (error) {
        console.error('Erreur chargement selection du tournoi:', error);
        displayErrorMessage('#content', error.message || 'Erreur lors du chargement de la vue de selection du tournoi.');
    }
}
