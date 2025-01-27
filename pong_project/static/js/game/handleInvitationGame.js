// game/invitations.js
import { requestPost, requestGet }  from '../api/index.js';
import { showStatusMessage, updateHtmlContent } from '../tools/index.js';
import { HTTPError } from '../api/index.js';
import { navigateTo } from '../router.js';

///////////////////////////////
//  PARTIE BURGER MENU
///////////////////////////////
export async function handleGameInvitationBurgerMenu(invitationId, action) {
    try {
        if (action === 'accept') {
            // On appelle AcceptGameInvitationView
            const url = `accept_invitation/${invitationId}`;
            const formData = new FormData();

            const response = await requestPost('game', url, formData);
            if (response.status === 'success') {
                console.log('Invitation acceptée => session créée :', response);
                // Supprime l'invitation de l'UI
                document.querySelector(`[data-invitation-id="${invitationId}"]`)
                    ?.closest('.invitation-item')
                    ?.remove();

                // Rediriger l'utilisateur (B) vers loading (SPA => adapter URL si besoin)
                navigateTo(`/game-loading`);
                //window.location.href = `/game/loading/${response.session.id}`;
            } else {
                console.error('Erreur à l\'acceptation :', response.message);
            }
        } 
        else if (action === 'decline') {
            // On appelle RespondToInvitationView
            const formData = new FormData();
            formData.append('invitation_id', invitationId);
            formData.append('action', 'decline');

            const response = await requestPost('game', 'respond_to_invitation', formData);
            if (response.status === 'success') {
                console.log('Invitation refusée :', response);
                document.querySelector(`[data-invitation-id="${invitationId}"]`)
                    ?.closest('.invitation-item')
                    ?.remove();
            } else {
                console.error('Erreur lors du refus :', response.message);
            }
        }
    } catch (error) {
        console.error('Erreur réseau lors du traitement de l\'invitation :', error);
    }
}


///////////////////////////////
//  PARTIE INVITATION ONLINE
///////////////////////////////
let cachedOnlineParams = null;

/**
 * Fonction appelée quand on clique sur "Inviter un ami" dans la section "online".
 * On reçoit les paramètres (ball_speed, racket_size, etc.), on affiche la liste d'amis.
 */
export async function handleInviteGame(onlineParams) {
    console.log('[handleInviteGame] Paramètres online = ', onlineParams);

    cachedOnlineParams = onlineParams;

    try {
        const response = await requestGet('game', 'invite_game'); 
        if (response.status === 'error') {
            showStatusMessage(response.message, 'error');
        } else {
            updateHtmlContent('#content', response.html);
            // Optionnel : si tu veux lancer le polling direct
                    // (pour que A voie en temps quasi-réel l'acceptation)
            startWaitingRoomPolling();
            initializeFriendInvitationBtn();
        }
    } catch (error) {
        if (error instanceof HTTPError) {
            showStatusMessage(error.message, 'error');
        } else {
            showStatusMessage('Une erreur est survenue.', 'error');
        }
        console.error('Erreur handleInviteGame :', error);
    }
}

function initializeFriendInvitationBtn() {
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
            await sendInvitation(btn);
        }
    });
}

async function sendInvitation(button) {
    console.log('[sendInvitation] Envoi de l\'invitation...');
    const friendUsername = button.closest('li')?.getAttribute('data-username');
    if (!friendUsername) {
        console.error('Nom d\'utilisateur introuvable.');
        return;
    }

    const formData = new FormData();
    formData.append('friend_username', friendUsername);

    // On inclut les params récupérés en "cachedOnlineParams"
    if (cachedOnlineParams) {
        formData.append('ball_speed',               cachedOnlineParams.ball_speed);
        formData.append('racket_size',             cachedOnlineParams.racket_size);
        formData.append('bonus_malus_activation',  cachedOnlineParams.bonus_malus_activation);
        formData.append('bumpers_activation',      cachedOnlineParams.bumpers_activation);
    } else {
        console.warn('Aucun paramètre en cache.');
    }

    try {
        const response = await requestPost('game', 'send_invitation', formData);
        if (response.status === 'success') {
            button.innerHTML = 'Envoyé <span class="cancel-icon">&times;</span>';
            button.classList.add('sent');
            button.disabled = false;
        } else {
            throw new Error(response.message || 'Erreur inconnue');
        }
    } catch (error) {
        console.error('Erreur lors de l\'envoi :', error);
        button.textContent = 'Erreur';
        button.classList.add('error');
        setTimeout(() => {
            button.innerHTML = 'Inviter <span class="cancel-icon d-none">&times;</span>';
            button.classList.remove('error');
        }, 3000);
    }
}

async function cancelInvitation(button) {
    const friendBtn = button.parentElement.querySelector('.friend-btn');
    const friendUsername = friendBtn ? friendBtn.textContent : null;
    if (!friendUsername) return;

    console.log('[cancelInvitation] Annulation invitation à', friendUsername);
    const formData = new FormData();
    formData.append('friend_username', friendUsername);

    try {
        const response = await requestPost('game', 'cancel_invitation', formData);
        if (response.status === 'success') {
            button.innerHTML = 'Inviter';
            button.classList.remove('sent');
        }
    } catch (error) {
        console.error('Erreur annulation invitation:', error);
    }
}


///////////////////////////////
//  POLLING OPTIONNEL
///////////////////////////////
let pollInterval = null;

export function startWaitingRoomPolling() {
    if (pollInterval) return; // Déjà en cours ?

    pollInterval = setInterval(pollInvitations, 3000);
}

async function pollInvitations() {
    try {
        const response = await requestGet('game', 'list_invitations');
        if (response.status === 'success') {
            const sent = response.data.sent_invitations;
            // Chercher si une invitation est accepted + a un session_id
            const accepted = sent.find(inv => inv.status === 'accepted' && inv.session_id != null);

            if (accepted) {
                clearInterval(pollInterval);
                pollInterval = null;

                // Redirige vers /game/loading/<session_id>
                navigateTo(`/game-loading`);
                //window.location.href = `/game/loading/${accepted.session_id}`;
            }
        }
    } catch (error) {
        console.error('Erreur polling invitations:', error);
    }
}
