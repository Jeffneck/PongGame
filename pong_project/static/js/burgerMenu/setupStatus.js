import { requestPost } from '../api/index.js';
import { showStatusMessage } from '../tools/index.js';

async function updateUserStatus(status) {
    console.log('Mise à jour du statut utilisateur :', status);

    const formData = new FormData();
    formData.append('status', status);

    try {
        const response = await requestPost('accounts', 'burgerMenu/update-status', formData);
        if (response.status !== 'success') {
            throw new Error(response.message || 'Erreur inconnue lors de la mise à jour du statut.');
        }
        console.log(`Statut mis à jour avec succès : ${status}`);
        return response; // Retourne la réponse pour une éventuelle utilisation
    } catch (error) {
        console.error('Erreur dans updateUserStatus :', error);
        throw error; // Relance l'erreur pour la gérer ailleurs
    }
}

export async function handleStatusChange(status) {
    try {
        await updateUserStatus(status);
        showStatusMessage('Statut mis à jour avec succès.', 'success');
        console.log('Statut mis à jour avec succès dans l\'interface utilisateur.');
    } catch (error) {
        console.error('Erreur lors de la mise à jour du statut :', error);
        showStatusMessage('Impossible de mettre à jour le statut. Veuillez réessayer.', 'error');
    }
}
