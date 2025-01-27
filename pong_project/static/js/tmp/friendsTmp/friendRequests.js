import { loadBurgerMenuData } from '../navbar/loadBurgerMenuData.js';
import { requestGet, requestPost }  from '../api/index.js';


/**
 * Vide la liste des demandes d'amis.
 * @param {HTMLElement} container - L'élément HTML qui contient la liste des demandes.
 */
function clearFriendRequestsList(container) {
    container.innerHTML = '';
}


/**
 * Affiche un message indiquant qu'il n'y a aucune demande d'ami.
 * @param {HTMLElement} container - L'élément HTML qui contient la liste des demandes.
 */
function renderNoFriendRequests(container) {
    container.innerHTML = '<p class="text-center">Aucune invitation pour le moment.</p>';
}


/**
 * Crée un élément de demande d'ami à partir du template #friend-request-item-template
 * @param {Object} request - Objet représentant la demande (id, from_user, avatar_url)
 * @returns {HTMLElement} Un fragment DOM prêt à être inséré dans la liste
 */
function createRequestItem(request) {
    const template = document.getElementById('friend-request-item-template');
    const clone = template.content.cloneNode(true);

    // Mettre à jour le contenu du clone avec les données de la requête
    const avatar = clone.querySelector('.request-avatar');
    avatar.src = request.avatar_url;

    const fromUserElem = clone.querySelector('.request-from-user');
    fromUserElem.textContent = request.from_user;

    // Boutons accept/refuse
    const acceptBtn = clone.querySelector('.request-accept-btn');
    acceptBtn.setAttribute('data-request-id', request.id);
    acceptBtn.setAttribute('data-action', 'accept');

    const declineBtn = clone.querySelector('.request-decline-btn');
    declineBtn.setAttribute('data-request-id', request.id);
    declineBtn.setAttribute('data-action', 'decline');

    return clone;
}


/**
 * Ajoute un élément (une demande) à la liste des demandes.
 * @param {HTMLElement} container - L'élément HTML qui contient la liste des demandes.
 * @param {Object} request - L'objet demande d'ami.
 */
function addRequestItemToList(container, request) {
    const requestItem = createRequestItem(request);
    container.insertAdjacentHTML('beforeend', requestItem);
}


/**
 * Traite une demande d'ami (accepter ou refuser).
 * @param {string} requestId - L'ID de la demande d'ami.
 * @param {string} action - L'action à effectuer ('accept' ou 'decline').
 * Envoie les données au serveur et renvoie un objet contenant le statut et un message.
 * @returns {Promise<{success: boolean, message: string}>} - Un objet indiquant le succès et un message.
 */
export async function handleFriendRequest(requestId, action) {
    const formData = new FormData();
    formData.append('request_id', requestId);
    formData.append('action', action);

    try {
        const response = await requestPost('/accounts/handle_friend_request/', formData);
        
        if (response.status === 'success') {
            return { success: true, message: `Invitation ${action}ée avec succès.` };
        } else {
            return { success: false, message: response.error || 'Une erreur est survenue.' };
        }
    } catch (error) {
        return { success: false, message: error.message || 'Erreur traitement invitation.' };
    }
}


/**
 * Ajoute des écouteurs d'événements sur les boutons d'acceptation/refus de demande.
 * Lorsqu'un bouton est cliqué, appelle handleFriendRequest, affiche un message, et recharge le burger menu.
 * @param {HTMLElement} container - L'élément HTML qui contient la liste des demandes.
 */
function attachEventListeners(container) {
    container.querySelectorAll('button[data-request-id]').forEach(btn => {
        btn.addEventListener('click', async () => {
            const requestId = btn.getAttribute('data-request-id');
            const action = btn.getAttribute('data-action');
            
            const result = await handleFriendRequest(requestId, action);
            if (result.success) {
                alert(result.message);
                await loadBurgerMenuData();
            } else {
                console.error('Erreur:', result.message);
            }
        });
    });
}

/**
 * MAIN FUNCTION
 * Met à jour la liste des demandes d'amis dans le DOM en utilisant le template #friend-request-item-template.
 * Si aucune demande n'est présente, affiche un message. Sinon, crée un élément pour chaque demande,
 * l'insère dans la liste, et attache les événements sur les boutons accept/refuse.
 * @param {Array} friendRequests - Tableau de demandes d'amis ({id, from_user, avatar_url}).
 */
export function updateFriendRequestsList(friendRequests) {
    const friendRequestsListElement = document.getElementById('friend-requests-list-container');
    if (!friendRequestsListElement) return;

    clearFriendRequestsList(friendRequestsListElement);

    if (!friendRequests || friendRequests.length === 0) {
        renderNoFriendRequests(friendRequestsListElement);
    } else {
        friendRequests.forEach(request => addRequestItemToList(friendRequestsListElement, request));
        attachEventListeners(friendRequestsListElement);
    }
}
