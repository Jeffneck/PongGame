import { requestPost } from '../../api/index.js';
import {showStatusMessage} from '../../tools/index.js';

async function addFriend(friendUsername) {
    console.log('addFriend:', friendUsername);

    const formData = new FormData();
    formData.append('friend_username', friendUsername);

    try {
        const response = await requestPost('accounts', 'friends/add', formData);
        if (!response || response.status !== 'success') {
            const errorMessage = response?.message || 'Erreur inconnue lors de l\'ajout de l\'ami.';
            console.error('Erreur dans addFriend:', errorMessage);
            throw new Error(errorMessage);
        }
        return response;
    } catch (error) {
        console.error('Exception dans addFriend:', error);
        throw error; // Relance l'erreur pour qu'elle soit gérée ailleurs
    }
}

export async function handleAddFriend(e) {
    e.preventDefault();
    console.log('Gestionnaire: handleAddFriend - Ajout d\'un ami');
    const friendUsernameInput = document.querySelector('#friend-username');
    if (!friendUsernameInput) {
        showStatusMessage('Champ utilisateur introuvable.', 'error');
        return;
    }

    const friendUsername = friendUsernameInput.value.trim();

    if (!friendUsername) {
        showStatusMessage('Le nom d\'utilisateur ne peut pas être vide.', 'error');
        return;
    }

    console.log('Gestionnaire: handleAddFriend - Ajout d\'un ami:', friendUsername);

    try {
        await addFriend(friendUsername);
        showStatusMessage('Demande d\'ami envoyée avec succès.', 'success');
    } catch (error) {
        const errorMessage = error?.message || 'Une erreur inattendue est survenue.';
        console.error('Erreur dans handleAddFriend:', error);
        showStatusMessage(errorMessage, 'error');
    }
}
    