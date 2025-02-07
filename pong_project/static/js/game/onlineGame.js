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

        // Si pas déjà envoyé
        if (!btn.classList.contains('sent')) {
            await sendInvitation(btn, game_id);
        }
    });
}


// cette fonction est lancée par la fonction checkGameInvitation status quand le joueur right a accepté l'invitation
// elle redirige le joueur left (celui qui a envoyé l'invitation) vers la page de jeu
// sur la page de jeu le joueur pourra cliquer sur un bouton qui lancera le jeu en arrière plan (cf.live_online_game_left.js)
async function joinOnlineGameAsLeft(game_id){
    try {
        const response = await requestGet('game', `join_online_game_as_left/${game_id}`); 
        if (response.status === 'success') {
            // afficher le html de la page de jeu
            updateHtmlContent('#content', response.html);
            // afficher le front du jeu au joueur left & transmettre les inputs du joueur left au jeu
            // le button startGame de live_online_game_as_left.html permettra de lancer l'algo du jeu en back depuis le js de liveOnlineGameLeft()
            await launchLiveGameWithOptions(game_id, 'left', `start_online_game/${game_id}`);
            const statusResponse = await requestGet('game', `get_game_status/${game_id}`);
            if (statusResponse.status === 'success' && statusResponse.session_status === 'cancelled') {
                showStatusMessage('Un des joueurs s\'est deconnecte, partie annulee ...', 'error');
                return
            }
            if (statusResponse.status === 'error' ) {
                showStatusMessage('Vous avez ete deconnecte de la partie en ligne', 'error');
                return
            }
            await showResults(game_id);
            
            //IMPROVE afficher une page présentant le winner et looser une fois la game terminee
        } else {
            showStatusMessage(response.message, 'error');
        }
    } catch (error) {
        if (error instanceof HTTPError) {
            showStatusMessage(error.message, 'error');
        } else {
            showStatusMessage('Une erreur est survenue.', 'error');
        }
        console.error('Erreur joinOnlineGameAsLeft :', error);
    }
  };



// async function joinOnlineGameAsLeft(game_id) {
//   try {
//     const tactile = isTouchDevice();
//     const formData = new FormData();
//     formData.append('is_touch', tactile);
//     const url = `join_online_game_as_left/${game_id}`;
//     const response = await requestPost('game', url, formData);
//     if (response.status === 'success') {
//       updateHtmlContent('#content', response.html);
//       await launchLiveGameWithOptions(game_id, 'left', `start_online_game/${game_id}`);
//       await showResults(game_id);
//     } else {
//       showStatusMessage(response.message, 'error');
//     }
//   } catch (error) {
//     console.error('Erreur dans joinOnlineGameAsLeft :', error);
//     showStatusMessage(error.message || 'Erreur réseau.', 'error');
//   }
// }

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

// lancee par acceptGameInvitation() 
// rediriger le joueur ayant accepté l'invitation vers la page de jeu
async function joinOnlineGameAsRight(gameId) {
    try {
        // Récupérer les données pour rejoindre la partie
        const response = await requestGet('game', `join_online_game_as_right/${gameId}`);

        // Gestion des erreurs renvoyées par le serveur
        if (response.status === 'error') {
            console.error("Erreur lors de la tentative de rejoindre le jeu :", response.message);
            showStatusMessage(response.message, 'error');
            return;
        }
        // Si succès, afficher la page de jeu 
        updateHtmlContent('#content', response.html);
        await launchLiveGameWithOptions(gameId, 'right', `start_online_game/${gameId}`);
        // on vérifie le status côté serveur avant de continuer la loop
        const statusResponse = await requestGet('game', `get_game_status/${gameId}`);
        alert('get game status effectue')
        if (statusResponse.status === 'success' && statusResponse.session_status === 'cancelled') {
            showStatusMessage('Un des joueurs s\'est deconnecte, partie annulee ...', 'error');
            return
        }
        alert('ne devrait pas apparaitre')
        if (statusResponse.status === 'error' ) {
            showStatusMessage('Vous avez ete deconnecte de la partie en ligne', 'error');
            return
        }
        await showResults(gameId);


    } catch (error) {
        console.error('Erreur réseau lors de la connexion au jeu en tant que joueur Right:', error);
        showStatusMessage('Une erreur réseau est survenue. Veuillez réessayer.', 'error');
    }
  };


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

