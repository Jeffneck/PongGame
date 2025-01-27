import { clearSessionAndUI, showStatusMessage } from '../tools/index.js';
import { requestPost } from '../api/index.js';

async function logoutUser() {
    try {
        const formData = new FormData();
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
            throw new Error('Aucun refresh token trouvé.');
        }
        formData.append('refresh_token', refreshToken);
        const response = await requestPost('accounts', 'logout', formData);

        if (response.status !== 'success') {
            throw new Error('La déconnexion a échoué côté serveur.');
        }
        return response;
    } catch (error) {
        console.error('Erreur lors de logoutUser :', error);
        throw error;
    }
}

export async function handleLogout() {
    console.log('Déconnexion en cours...');
    try {
        await logoutUser();
        showStatusMessage('Votre compte a été déconnecté avec succès.', 'success');
        setTimeout(() => {
            clearSessionAndUI();
        }, 3000);
        console.log('Déconnexion réussie.');
    } catch (error) {
        console.error('Erreur lors de la déconnexion :', error);
        showStatusMessage('La déconnexion a échoué. Veuillez réessayer.', 'error');
    }
}
