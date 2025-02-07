"use strict";
import { toggleBurgerMenu } from './toggleBurgerMenu.js';
import { requestGet } from '../api/index.js';
import { updateHtmlContent, showStatusMessage } from '../tools/index.js';
import { initBurgerMenuDelegation } from './delegation.js';
import { eventsHandlerBurgerMenu } from '../burgerMenu/index.js';
import { navigateTo } from '../router.js';

async function initializeBurgerMenu(flag) {
  const burgerToggle = document.querySelector('#burger-menu-toggle');
  if (burgerToggle && !burgerToggle.dataset.bound) {
    burgerToggle.addEventListener('click', () => toggleBurgerMenu(flag));
    burgerToggle.dataset.bound = true;
    console.debug('Burger menu events initialisés.');
  }
}

function handleHomeButtonClick(isAuthenticated) {
  if (isAuthenticated) navigateTo('/home');
  else navigateTo('/');
}

async function loadNavbar() {
  try {
    console.debug('Chargement de la navbar...');
    const data = await requestGet('core', 'navbar');
    if (data && data.html) {
      updateHtmlContent('#navbar', data.html);
      const homeButton = document.querySelector('#home-btn');
      if (homeButton && !homeButton.dataset.bound) {
        homeButton.addEventListener('click', () => handleHomeButtonClick(data.is_authenticated));
        homeButton.dataset.bound = true;
      }
      return data.is_authenticated;
    } else {
      console.error("Contenu de la navbar manquant.");
      showStatusMessage('Impossible de charger la barre de navigation.', 'error');
      return false;
    }
  } catch (error) {
    console.error('Erreur dans loadNavbar:', error);
    showStatusMessage('Erreur lors du chargement de la navbar.', 'error');
    throw error;
  } finally {
    console.debug('Fin de loadNavbar.');
  }
}

export async function refreshBurgerMenu() {
  try {
    let menu = document.getElementById('burger-menu');
    let overlay = document.getElementById('overlay');
    if (!menu || !overlay) return;
    const data = await requestGet('accounts', 'burgerMenu');
    if (data.status === 'success') {
      if (menu.style.display === 'block') {
        updateHtmlContent('#burger-menu-container', data.html);
        menu = document.getElementById('burger-menu');
        overlay = document.getElementById('overlay');
        menu.style.display = 'block';
        overlay.style.display = 'block';
      } else {
        updateHtmlContent('#burger-menu-container', data.html);
        menu = document.getElementById('burger-menu');
        overlay = document.getElementById('overlay');
        menu.style.display = 'none';
        overlay.style.display = 'none';
      }
      await initializeBurgerMenu('refresh btn');
      eventsHandlerBurgerMenu();
      console.debug('Burger menu mis à jour.');
    } else {
      console.warn('Erreur lors de la mise à jour du burger menu:', data.status);
    }
  } catch (error) {
    console.error('Erreur dans refreshBurgerMenu:', error);
  }
}


export async function handleNavbar() {
  try {
    console.debug('Chargement de la navbar...');
    const is_authenticated = await loadNavbar();
    if (is_authenticated) {
      await initializeBurgerMenu(null);
      initBurgerMenuDelegation();
      eventsHandlerBurgerMenu();
      setInterval(refreshBurgerMenu, 10000);
    }
  } catch (error) {
    console.error('Erreur dans handleNavbar:', error);
    showStatusMessage('Erreur lors du chargement de la navbar.', 'error');
  }
}
