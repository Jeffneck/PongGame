//friends/friendActions.js
//fonctions actuellement inutilisees dans le code

import { requestGet, requestPost, requestDelete }  from '../api/index.js';


/**
 * Envoie une demande d'ami à un utilisateur spécifique.
 * @param {string} toUserId - L'identifiant (ID) de l'utilisateur à qui envoyer la demande.
 * Effectue un appel API pour envoyer la demande, affiche un message, puis rafraîchit la liste d'amis.
 * En cas d'erreur, affiche une alerte d'erreur.
 */
export async function sendFriendRequest(toUserId) {
    try {
        const response = await requestPost('accounts',`send_friend_request/${toUserId}/`, null);
        alert(response.message);
        refreshFriendsList();
    } catch (error) {
        alert('Erreur lors de l\'envoi de la demande: ' + (error.message || ''));
    }
}


/**
 * Supprime un ami de la liste d'amis de l'utilisateur.
 * @param {string} friendId - L'identifiant (ID) de l'ami à supprimer.
 * Effectue un appel API pour retirer l'ami, affiche un message, puis rafraîchit la liste d'amis.
 * En cas d'erreur, affiche une alerte d'erreur.
 */
export async function removeFriend(friendId) {
    try {
        const response = await requestDelete('accounts', 'remove_friend', friendId);
        alert(response.message);
        refreshFriendsList();
    } catch (error) {
        alert('Erreur suppression ami: ' + (error.message || ''));
    }
}

/**
 * Cette fonction utilise le template #friend-item-template pour créer un élément d'ami,
 * met à jour ses propriétés en fonction des données `friend`, puis le renvoie pour insertion dans le DOM.
 * @param {Object} friend - Données de l'ami (username, avatar_url, status)
 * @returns {HTMLElement} L'élément <li> configuré.
 */
function createFriendItem(friend) {
    // Récupère le template du DOM
    const template = document.getElementById('friend-item-template');
    // Clone le contenu du template
    const clone = template.content.cloneNode(true);

    // Met à jour les champs
    const avatar = clone.querySelector('.friend-avatar');
    avatar.src = friend.avatar_url;

    const statusIndicator = clone.querySelector('.status-indicator-friend');
    statusIndicator.classList.add(friend.status === 'online' ? 'online' : 'offline');

    const friendBtn = clone.querySelector('.friend-btn');
    friendBtn.textContent = friend.username;
    friendBtn.setAttribute('data-username', friend.username);

    return clone;
}


/**
 * Rafraîchit la liste des amis en utilisant le template #friend-item-template.
 * Pour chaque ami récupéré de l'API, on clone le template, met à jour ses données, puis on l'ajoute au conteneur.
 */
export async function refreshFriendsList() {
    try {
        const data = await requestGet('accounts', 'get_burger_menu_data');
        const friendsListContainer = $('#friends-list-container');
        friendsListContainer.empty();

        if (data.friends && data.friends.length > 0) {
            data.friends.forEach(friend => {
                // Crée l'élément ami à partir du template
                const friendItem = createFriendItem(friend);
                // friendItem est un DocumentFragment, on l'insère dans le DOM
                friendsListContainer.append(friendItem);
            });
        } else {
            friendsListContainer.html('<p class="text-center">Aucun ami pour le moment.</p>');
        }
    } catch (error) {
        console.error('Erreur rafraichissement liste amis:', error);
        $('#friends-list-container').html('<p class="text-center text-danger">Erreur de chargement.</p>');
    }
}
