import { initializeHomeView } from './landing/coreHome.js';
import { handleLogin, initializeRegisterView, initializeLogin2FAView, handleDisable2FA, handleEnable2FA } from './auth/index.js';
import { handleInviteGame, initializeGameHomeView } from './game/index.js';
import { handleAccountsManagement } from './accountManagement/index.js';
import { handleViewProfile } from './userProfile/index.js';
import {handleGameMenu} from './game/index.js';
import { handleFriendProfile } from './friends/index.js';
import { handleNavbar } from './navbar/loadNavbar.js';

// Initialisation du routeur Navigo
const router = new window.Navigo('/', { hash: false });


/**
 * Initialisation des routes Navigo.
 */
export function initializeRouter() {
    router
        .on('/', () => {
            console.log('Route: Home');
            handleNavbar();
            initializeHomeView();
        })
        .on('/login', () => {
            console.log('Route: Login');
            handleLogin();
        })
        .on('/login-2fa', () => {
            console.log('Route: Login');
            initializeLogin2FAView();
        })
        .on('/register', () => {
            console.log('Route: Register');
            initializeRegisterView();
        })
        .on('/enable-2fa', () => {
            console.log('Route: 2FA Login');
            handleEnable2FA();
        })
        .on('/disable-2fa', () => {
            console.log('Route: 2FA Login');
            handleDisable2FA();
        })
        .on('/home', () => {
            console.log('Route: Game Home');
            initializeGameHomeView();
        })
        .on('/account', () => {
            console.log('Route: account');
            handleAccountsManagement();
        })
        .on('/profile', () => {
            console.log('Route: profile');
            handleViewProfile();
        })
        .on('/game-options', () => {
            console.log('Route: game-options');
            handleGameMenu();
        })
        .on('/game-online', () => {
            console.log('Route: game-options');
            handleInviteGame();
        
        })
        .on('/game-loading', () => {
            console.log('Route: game-options');
            startLoading();
        })


        .on('/profile/:friendUsername', ({ data }) => {
            const friendUsername = data.friendUsername; // Utilisez `data` pour extraire le paramètre
            console.log(`Route: Profile for ${friendUsername}`);
            handleFriendProfile(friendUsername);
        })
        .notFound(() => {
            console.error('Route inconnue : Page non trouvée');
            // Charger une vue 404 ici si nécessaire
        });

    // Résolution de la route actuelle
    router.resolve();
}

/**
 * Navigation dynamique.
 * @param {string} route - La route cible.
 */
export function navigateTo(route) {
    console.log(`Navigation vers ${route}`);
    router.navigate(route);
}
