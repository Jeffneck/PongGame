
// Fonctions génériques pour l'affichages d'informations
export { displayErrorMessage, displaySuccessMessage, clearMessage, displayInfoMessage, showStatusMessage } from './displayInfo.js';

export { updateTextContent, updateAttribute , updateHtmlContent} from './domHandler.js';
export { isTouchDevice, resetScrollPosition } from './utility.js';

// Fonction générique, supprime les tokens et remet à zéro l'interface utilisateur
export {clearSessionAndUI} from './clearSession.js';
