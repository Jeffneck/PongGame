"use strict";
import { requestGet, requestPost } from "../api/index.js";
import { updateHtmlContent, showStatusMessage } from "../tools/index.js";
import { isTouchDevice } from "../tools/utility.js";
import { initializeGameControls } from "./controls.js";
import { launchLiveGameWithOptions } from "./live_game.js";
import { showResults } from "./gameResults.js";
import { navigateTo } from "../router.js";

export async function createGameOnline() {
  try {
    if (!localStorage.getItem('access_token')) {
      navigateTo('/');
      return;
    }
    let onlineParams = sessionStorage.getItem('params');
    if (!onlineParams) {
      showStatusMessage("Paramètres online invalides.", 'error');
      navigateTo('/game-options');
      return;
    }
    try {
      onlineParams = JSON.parse(onlineParams);
    } catch (e) {
      showStatusMessage("Erreur lors de la récupération des paramètres.", 'error');
      return;
    }
    const formData = new FormData();
    formData.append('ball_speed', onlineParams.ball_speed);
    formData.append('paddle_size', onlineParams.paddle_size);
    formData.append('bonus_enabled', onlineParams.bonus_enabled);
    formData.append('obstacles_enabled', onlineParams.obstacles_enabled);
    const response = await requestPost('game', 'create_game_online', formData);
    if (response.status === 'error') {
      showStatusMessage(response.message, 'error');
    } else {
      updateHtmlContent('#content', response.html);
      initializeFriendInvitationBtn(response.game_id);
    }
  } catch (error) {
    console.error('Erreur dans createGameOnline :', error);
    showStatusMessage('Erreur lors de la création de la partie en ligne.', 'error');
  }
}

async function sendInvitation(button, game_id) {
  const friendUsername = button.closest('li')?.getAttribute('data-username');
  if (!friendUsername) {
    console.error('Nom d\'utilisateur introuvable.');
    return;
  }
  const formData = new FormData();
  formData.append('friend_username', friendUsername);
  try {
    button.disabled = true;
    const response = await requestPost('game', 'send_invitation', formData);
    if (response.status === 'success') {
      button.innerHTML = 'Envoyé <span class="cancel-icon">&times;</span>';
      button.classList.add('sent');
    } else {
      throw new Error(response.message || 'Erreur inconnue');
    }
  } catch (error) {
    console.error('Erreur dans sendInvitation:', error);
    button.textContent = 'Erreur';
    button.classList.add('error');
    setTimeout(() => {
      button.innerHTML = 'Inviter <span class="cancel-icon d-none">&times;</span>';
      button.classList.remove('error');
    }, 3000);
  } finally {
    button.disabled = false;
  }
}

async function cancelInvitation(button) {
  const friendName = button.parentElement.querySelector('.friend-btn')?.textContent;
  if (!friendName) return;
  const formData = new FormData();
  formData.append('friend_username', friendName);
  try {
    const response = await requestPost('game', 'cancel_invitation', formData);
    if (response.status === 'success') {
      button.innerHTML = 'Inviter';
      button.classList.remove('sent');
    }
  } catch (error) {
    console.error('Erreur dans cancelInvitation:', error);
  }
}

let pollInterval = null;
export function startWaitingRoomPolling() {
  if (pollInterval) return;
  pollInterval = setInterval(async () => {
    try {
      const response = await requestGet('game', 'list_invitations');
      if (response.status === 'success') {
        const sent = response.data.sent_invitations;
        const accepted = sent.find(inv => inv.status === 'accepted' && inv.session_id != null);
        if (accepted) {
          clearInterval(pollInterval);
          pollInterval = null;
          navigateTo(`/game-loading`);
        }
      }
    } catch (error) {
      console.error('Erreur pendant le polling des invitations:', error);
      clearInterval(pollInterval);
    }
  }, 3000);
}

function initializeFriendInvitationBtn(game_id) {
  document.addEventListener('click', async (event) => {
    const btn = event.target.closest('.invite-button');
    if (!btn) return;
    if (event.target.classList.contains('cancel-icon')) {
      event.stopPropagation();
      await cancelInvitation(btn);
      return;
    }
    if (!btn.classList.contains('sent')) {
      await sendInvitation(btn, game_id);
    }
  });
}

async function joinOnlineGameAsLeft(game_id) {
  try {
    const tactile = isTouchDevice();
    const formData = new FormData();
    formData.append('is_touch', tactile);
    const url = `join_online_game_as_left/${game_id}`;
    const response = await requestPost('game', url, formData);
    if (response.status === 'success') {
      updateHtmlContent('#content', response.html);
      await launchLiveGameWithOptions(game_id, 'left', `start_online_game/${game_id}`);
      await showResults(game_id);
    } else {
      showStatusMessage(response.message, 'error');
    }
  } catch (error) {
    console.error('Erreur dans joinOnlineGameAsLeft :', error);
    showStatusMessage(error.message || 'Erreur réseau.', 'error');
  }
}

export async function acceptGameInvitation(invitationId, action) {
  try {
    if (action === 'accept') {
      const url = `accept_game_invitation/${invitationId}`;
      const response = await requestPost('game', url, new FormData());
      if (response.status === 'success') {
        document.querySelector(`[data-invitation-id="${invitationId}"]`)?.closest('.invitation-item')?.remove();
        joinOnlineGameAsRight(response.session.id);
      } else {
        console.error('Erreur à l\'acceptation:', response.message);
      }
    } else if (action === 'decline') {
      await declineGameInvitation(invitationId);
    }
  } catch (error) {
    console.error('Erreur dans acceptGameInvitation:', error);
  }
}

async function joinOnlineGameAsRight(sessionId) {
  try {
    const tactile = isTouchDevice();
    const formData = new FormData();
    formData.append('is_touch', tactile);
    const url = `join_online_game_as_left/${sessionId}`;
    const response = await requestPost('game', url, formData);
    if (response.status === 'success') {
      updateHtmlContent('#content', response.html);
      await launchLiveGameWithOptions(response.game_id, 'right', `start_online_game/${response.game_id}`);
      await showResults(response.game_id);
    } else {
      showStatusMessage(response.message, 'error');
    }
  } catch (error) {
    console.error('Erreur dans joinOnlineGameAsRight:', error);
    showStatusMessage('Erreur réseau. Veuillez réessayer.', 'error');
  }
}

export async function declineGameInvitation(invitationId) {
  try {
    const formData = new FormData();
    formData.append('invitation_id', invitationId);
    formData.append('action', 'decline');
    const url = `reject_game_invitation/${invitationId}`;
    const response = await requestPost('game', url, formData);
    if (response.status === 'success') {
      document.querySelector(`[data-invitation-id="${invitationId}"]`)?.closest('.invitation-item')?.remove();
    } else {
      console.error('Erreur lors du refus:', response.message);
    }
  } catch (error) {
    console.error('Erreur dans declineGameInvitation:', error);
  }
}

