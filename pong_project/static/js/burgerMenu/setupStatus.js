"use strict";
import { requestPost } from '../api/index.js';
import { refreshBurgerMenu } from '../navbar/loadNavbar.js';
import { showStatusMessage } from '../tools/index.js';

async function updateUserStatus(status) {
  console.debug('Mise à jour du statut utilisateur :', status);
  const formData = new FormData();
  formData.append('status', status);
  try {
    const response = await requestPost('accounts', 'burgerMenu/update-status', formData);
    if (response.status !== 'success') {
      throw new Error(response.message || 'Erreur inconnue.');
    }
    console.debug(`Statut mis à jour : ${status}`);
    return response;
  } catch (error) {
    console.error('Erreur dans updateUserStatus :', error);
    throw error;
  }
}

export async function handleStatusChange(status) {
  try {
    await updateUserStatus(status);
    showStatusMessage('Statut mis à jour avec succès.', 'success');
  } catch (error) {
    console.error('Erreur lors de la mise à jour du statut :', error);
    showStatusMessage('Impossible de mettre à jour le statut. Veuillez réessayer.', 'error');
  }
  await refreshBurgerMenu();
}
