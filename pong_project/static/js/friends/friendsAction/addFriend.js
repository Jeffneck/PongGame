"use strict";
import { requestPost } from '../../api/index.js';
import { showStatusMessage } from '../../tools/index.js';

async function addFriend(friendUsername) {
  console.debug('addFriend:', friendUsername);
  const formData = new FormData();
  formData.append('friend_username', friendUsername);
  try {
    const response = await requestPost('accounts', 'friends/add', formData);
    if (!response || response.status !== 'success') {
      const errorMessage = response?.message || 'Erreur lors de l\'ajout de l\'ami.';
      throw new Error(errorMessage);
    }
    return response;
  } catch (error) {
    console.error('Erreur dans addFriend:', error);
    throw error;
  }
}

export async function handleAddFriend(e) {
  e.preventDefault();
  const friendUsernameInput = document.querySelector('#friend-username');
  const addFriendButton = document.querySelector('#add-friend-button');
  if (!friendUsernameInput || !addFriendButton) {
    showStatusMessage('Champ ou bouton introuvable.', 'error');
    return;
  }
  const friendUsername = friendUsernameInput.value.trim();
  if (!friendUsername) {
    showStatusMessage('Le nom d\'utilisateur ne peut pas être vide.', 'error');
    return;
  }
  try {
    addFriendButton.disabled = true;
    await addFriend(friendUsername);
    showStatusMessage('Demande d\'ami envoyée avec succès.', 'success');
  } catch (error) {
    showStatusMessage(error?.message || 'Erreur inattendue.', 'error');
  } finally {
    addFriendButton.disabled = false;
  }
}
