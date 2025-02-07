"use strict";
import { initializeHomeView } from './landing/coreHome.js';
import { handleLogin, initializeRegisterView, initializeLogin2FAView, handleDisable2FA, handleEnable2FA } from './auth/index.js';
import {  initializeGameHomeView, handleGameMenu, createGameOnline, handleTournament } from './game/index.js';
import { handleAccountsManagement } from './accountManagement/index.js';
import { handleViewProfile } from './userProfile/index.js';
import { handleNavbar } from './navbar/loadNavbar.js';
import { initializeNotFoundView } from './tools/errorPage.js';


// Initialisation du routeur Navigo
const router = new window.Navigo('/', { hash: false });

export function initializeRouter() {
  router
    .on('/', () => {
      handleNavbar();
      initializeHomeView();
    })
    .on('/login', () => { handleLogin(); })
    .on('/login-2fa', () => { initializeLogin2FAView(); })
    .on('/register', () => { initializeRegisterView(); })
    .on('/enable-2fa', () => { handleEnable2FA(); })
    .on('/disable-2fa', () => { handleDisable2FA(); })
    .on('/home', () => { initializeGameHomeView(); })
    .on('/account', () => { handleAccountsManagement(); })
    .on('/profile', () => { handleViewProfile(); })
    .on('/game-options', () => { handleGameMenu(); })
    .on('/online', () => { createGameOnline(); })
    .on('/tournament', () => { handleTournament(); })
    .on('/game-loading', () => { startLoading(); })
    .on('/profile/:friendUsername', ({ data }) => {
      const friendUsername = data.friendUsername;
      handleFriendProfile(friendUsername);
    })
    .notFound(() => { initializeNotFoundView(); });
  router.resolve();
}

export function navigateTo(route) {
    console.log(`Navigation vers ${route}`);

    //fermer le socket si une session de jeu est en cours 
    if (window.currentGameSocket && window.currentGameSocket.readyState === WebSocket.OPEN) {
        console.log('Fermeture de la WebSocket en cours...');
        window.currentGameSocket.close();
    }
    window.currentGameSocket = null;
    //si on etait dans une boucle de tournoi, on bloque l' affichage des pages suivantes
    window.stopTournamentFlow = true;

    router.navigate(route);
}
