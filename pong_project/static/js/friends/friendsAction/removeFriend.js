import { requestPost } from '../../api/index.js';
import {showStatusMessage} from '../../tools/index.js';

async function removeFriend(friendName) {
    console.log(`removeFriend: Suppression de l'ami ${friendName}`);

    const formData = new FormData();
    formData.append('friend_username', friendName);

    try {
        const response = await requestPost('accounts', 'friends/remove', formData);
        if (!response || response.status !== 'success') {
            const errorMessage = response?.message || 'Erreur lors de la suppression de l\'ami.';
            console.error('Erreur dans removeFriend:', errorMessage);
            throw new Error(errorMessage);
        }
        return response;
    } catch (error) {
        console.error('Erreur dans removeFriend:', error);
        throw error;
    }
}

export async function handleRemoveFriend(friendName) {
    console.log(`Gestionnaire: handleRemoveFriend - Suppression de l'ami : ${friendName}`);
    try {
        const response = await removeFriend(friendName);
        document.querySelector(`.friend-btn:contains('${friendName}')`)?.closest('.friend-item')?.remove();
        showStatusMessage(response.message || 'Ami supprimé avec succès.', 'success');
    } catch (error) {
        const errorMessage = error?.message || 'Une erreur est survenue lors de la suppression de l\'ami.';
        console.error('Erreur dans handleRemoveFriend:', error);
        showStatusMessage(errorMessage, 'error');
    }
}
