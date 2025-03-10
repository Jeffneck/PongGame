"use strict";
import { requestPost } from '../../api/index.js';
import { showStatusMessage } from '../../tools/index.js';

async function friendInvitation(requestId, action) {
  console.debug(`Demande d'ami ID ${requestId}, action : ${action}`);
  const formData = new FormData();
  formData.append('request_id', requestId);
  formData.append('action', action);
  try {
    const response = await requestPost('accounts', 'friends/handle-request', formData);
    if (!response || response.status !== 'success') {
      const errorMessage = response?.message || 'Erreur lors du traitement de la demande d\'ami.';
      throw new Error(errorMessage);
    }
    return response;
  } catch (error) {
    console.error('Erreur dans friendInvitation:', error);
    throw error;
  }
}

export async function handleFriendInvitation(requestId, action) {
  try {
    const response = await friendInvitation(requestId, action);
    showStatusMessage(response.message || 'Demande d\'ami traitée avec succès.', 'success');
  } catch (error) {
    showStatusMessage(error?.message || 'Erreur lors du traitement de la demande d\'ami.', 'error');
  }
}
