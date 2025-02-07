// auth/index.js

// Fonctions de déconnexion et suppression de compte
// Appelle une fonction générique pour nettoyer la session utilisateur
export { handleLogout} from './logout.js';
export { handleDeleteAccount } from './deleteAccount.js';

export { handleLogin } from './login.js';
export { initializeRegisterView } from './register.js';


// Export des vues 2FA
export { handleEnable2FA} from './2fa//2faEnable.js';
export { initializeLogin2FAView } from './2fa/2faLogin.js';
export { handleDisable2FA } from './2fa/2faDisable.js';
