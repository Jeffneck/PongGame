import { requestGet } from "../api/index.js";
import { updateHtmlContent, displayErrorMessage } from "../tools/index.js";
import { initializeaccountsManagementFormHandlers } from "./index.js";
import { showStatusMessage } from "../tools/index.js";
async function loadAccountsManagement() {
    try {
        const response = await requestGet('accounts', 'gestion_profil');
        if (response.status === 'success' && response.html) {
            updateHtmlContent('#content', response.html);
        }
        else {
            throw new Error(response.message || 'Erreur lors du chargement de la vue de gestion de profil.');
        }
    } catch (error) {
        console.error('Erreur chargement gestion profil:', error);
        showStatusMessage(error.message || 'Erreur lors du chargement de la vue de gestion de profil.', 'errors');
    }
}

export async function handleAccountsManagement() {
    try {
        await loadAccountsManagement();
        // Si votre backend renvoie directement du HTML, utilisez-le tel quel.
        // Sinon, adaptez en fonction de ce qui est renvoyé.
        initializeaccountsManagementFormHandlers();
    } catch (error) {
        console.error('Erreur chargement gestion profil:', error);
        showStatusMessage(error.message || 'Erreur lors du chargement de la vue de gestion de profil.', 'errors');
    }
}
