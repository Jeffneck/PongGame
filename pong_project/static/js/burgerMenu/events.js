"use strict";
import { showFriendPopup, closePopupOnClickOutside, handleOptionPopup, handleAddFriend, handleFriendInvitation } from '../friends/index.js';
import { handleStatusChange } from './setupStatus.js';
import { handleLogout } from '../auth/index.js';
import { navigateTo } from '../router.js';
import { acceptGameInvitation, declineGameInvitation } from '../game/index.js';

export function eventsHandlerBurgerMenu() {
  console.debug('Initialisation des événements du burger menu...');
  const container = document.getElementById('burger-menu-container');
  if (!container) {
    console.warn("Conteneur #burger-menu-container introuvable.");
    return;
  }
  if (!container.dataset.bound) {
    container.addEventListener('click', handleBurgerMenuClick);
    container.dataset.bound = 'true';
  }
  const addFriendForm = document.querySelector('#add-friend-form');
  if (addFriendForm && !addFriendForm.dataset.bound) {
    addFriendForm.addEventListener('submit', handleAddFriend);
    addFriendForm.dataset.bound = 'true';
  }
  const popup = document.getElementById('friendPopup');
  if (popup && !popup.dataset.bound) {
    document.addEventListener('click', closePopupOnClickOutside);
    popup.dataset.bound = 'true';
  }
  console.debug('Gestionnaire d\'événements du burger menu initialisé.');
}

function handleBurgerMenuClick(e) {
  if (e.target.matches('.status-selector button[data-status]')) {
    const status = e.target.dataset.status;
    if (status) handleStatusChange(status);
    return;
  }
  if (e.target.matches('#profile-btn')) {
    e.preventDefault();
    navigateTo('/profile');
    return;
  }
  if (e.target.matches('#play-btn')) {
    e.preventDefault();
    navigateTo('/game-options');
    return;
  }
  if (e.target.matches('#settings-link')) {
    e.preventDefault();
    navigateTo('/account');
    return;
  }
  const friendButton = e.target.closest('.friend-btn');
  if (friendButton) {
    showFriendPopup(e, friendButton.innerText.trim());
    return;
  }
  const friendRequestButton = e.target.closest('#friend-requests-list-container button[data-request-id]');
  if (friendRequestButton) {
    const requestId = friendRequestButton.getAttribute('data-request-id');
    const action = friendRequestButton.getAttribute('data-action');
    if (requestId) {
      handleFriendInvitation(requestId, action);
    }
    return;
  }
  const gameInvitationButton = e.target.closest('#game-invitations-list-container button[data-invitation-id]');
  if (gameInvitationButton) {
    const invitationId = gameInvitationButton.getAttribute('data-invitation-id');
    const action = gameInvitationButton.getAttribute('data-action');
    if (invitationId && action === 'accept') {
      acceptGameInvitation(invitationId, action);
    } else {
      declineGameInvitation(invitationId);
    }
    return;
  }
  if (e.target.matches('#view-profile-btn')) {
    handleOptionPopup('Voir le profil');
    return;
  }
  if (e.target.matches('#invite-to-play-btn')) {
    handleOptionPopup('Inviter à jouer');
    return;
  }
  if (e.target.matches('#remove-friend-btn')) {
    handleOptionPopup('Supprimer');
    return;
  }
  if (e.target.matches('#logout-btn')) {
    e.preventDefault();
    handleLogout();
    return;
  }
}
