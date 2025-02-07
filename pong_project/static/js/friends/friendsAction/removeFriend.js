"use strict";
import { requestPost } from '../../api/index.js';
import { showStatusMessage } from '../../tools/index.js';

async function removeFriend(friendName) {
  console.debug(`removeFriend: Suppression de ${friendName}`);
  const formData = new FormData();
  formData.append('friend_username', friendName);
  try {
    const response = await requestPost('accounts', 'friends/remove', formData);
    if (!response || response.status !== 'success') {
      const errorMessage = response?.message || 'Erreur lors de la suppression de l\'ami.';
      throw new Error(errorMessage);
    }
    return response;
  } catch (error) {
    console.error('Erreur dans removeFriend:', error);
    throw error;
  }
}

export async function handleRemoveFriend(friendName) {
  try {
    const response = await removeFriend(friendName);
    const friendButtons = document.querySelectorAll('.friend-btn');
    friendButtons.forEach((button) => {
      if (button.textContent.includes(friendName)) {
        button.closest('.friend-item')?.remove();
      }
    });
    showStatusMessage(response.message || 'Ami supprimé avec succès.', 'success');
  } catch (error) {
    showStatusMessage(error?.message || 'Erreur lors de la suppression de l\'ami.', 'error');
  }
}
