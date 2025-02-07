"use strict";
import { navigateTo } from '../router.js';
export function clearSessionAndUI(redirectUrl = '/') {
  console.debug('Nettoyage de la session et de l\'UI...');
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  const navbar = document.querySelector('#navbar');
  const burgerMenu = document.querySelector('#burger-menu');
  const content = document.querySelector('#content');
  if (navbar) navbar.innerHTML = '';
  if (burgerMenu) burgerMenu.innerHTML = '';
  if (content) content.innerHTML = '';
  navigateTo(redirectUrl);
  location.reload();
}
