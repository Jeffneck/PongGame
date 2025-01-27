import { requestGet } from '../../api/index.js';
import { updateHtmlContent, showStatusMessage } from '../../tools/index.js';


async function FriendProfile(friendName) {
    try {
        console.log(`Chargement du profil de l'ami : ${friendName}`);
        const response = await requestGet('accounts', `friend/${friendName}`);

        if (!response || response.status !== 'success') {
            const errorMessage = response?.message || 'Erreur lors de la récupération du profil.';
            console.error('Erreur dans FriendProfile :', errorMessage);
            throw new Error(errorMessage);
        }

        updateHtmlContent('#content', response.html);
        return response.message;
    } catch (error) {
        console.error('Erreur dans FriendProfile :', error);
        throw error;
    }
}

export async function handleFriendProfile(friendName) {
    console.log(`Gestionnaire: Affichage du profil de l'ami ${friendName}`);

    try {
        const response = await FriendProfile(friendName);
        showStatusMessage(response || 'Profil de l\'ami chargé avec succès.', 'success');
    } catch (error) {
        const errorMessage = error?.message || 'Erreur lors de la récupération du profil.';
        console.error('Erreur dans handleFriendProfile :', error);
        showStatusMessage(errorMessage, 'error');
    }
}
