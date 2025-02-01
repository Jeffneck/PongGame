

import { 
    showFriendPopup, 
    closePopupOnClickOutside, 
    handleOptionPopup,  
    handleAddFriend, 
    handleFriendInvitation  
} from '../friends/index.js';

import { handleStatusChange } from './index.js';
import { handleLogout } from '../auth/index.js';
import { navigateTo } from '../router.js';
import { acceptGameInvitation } from '../game/index.js';

/**
 * Gestionnaire principal des événements pour le menu burger via event delegation.
 * - Attache un seul listener "click" sur #burger-menu-container.
 * - Gère aussi le "submit" du formulaire d'ajout d'amis.
 */
export function eventsHandlerBurgerMenu() {
    console.log('Initialisation des gestionnaires d\'événements (event delegation)...');

    // 1. Récupérer le conteneur principal du burger menu
    const container = document.getElementById('burger-menu-container');
    if (!container) {
        console.warn("Impossible de trouver #burger-menu-container, annulation des events burger.");
        return;
    }

    // 2. Attacher UN SEUL listener "click" si pas déjà fait
    if (!container.dataset.bound) {
        container.addEventListener('click', handleBurgerMenuClick);
        container.dataset.bound = 'true';
        console.log("Listener 'click' sur #burger-menu-container initialisé.");
    }

    // 3. Gérer la soumission du formulaire d'ajout d'amis (événement "submit" distinct)
    const addFriendForm = document.querySelector('#add-friend-form');
    if (addFriendForm && !addFriendForm.dataset.bound) {
        addFriendForm.addEventListener('submit', handleAddFriend);
        addFriendForm.dataset.bound = 'true';
        console.log("Event 'submit' pour #add-friend-form attaché.");
    }

    // 4. Gérer la fermeture du popup d'ami au clic en dehors (hors du container burger)
    //    Ici, on peut écouter sur document ou sur un autre élément.
    const popup = document.getElementById('friendPopup');
    if (popup && !popup.dataset.bound) {
        document.addEventListener('click', closePopupOnClickOutside);
        popup.dataset.bound = 'true';
        console.log("Listener 'click' pour fermer le friendPopup en dehors.");
    }

    console.log('Event delegation pour le burger menu : terminé.');
}

/**
 * Fonction centrale qui gère tous les clics à l'intérieur de #burger-menu-container.
 */
function handleBurgerMenuClick(e) {
    // 1. Changement de statut (en ligne/hors ligne)
    //    Les boutons ont la classe .status-selector et un data-status
    if (e.target.matches('.status-selector button[data-status]')) {
        const status = e.target.dataset.status;
        if (status) handleStatusChange(status);
        return;
    }

    // 2. Bouton "Voir le profil" (#profile-btn)
    if (e.target.matches('#profile-btn')) {
        e.preventDefault();
        console.log('Profil bouton cliqué');
        navigateTo('/profile');
        return;
    }

    // 3. Navigation : Jouer (#play-btn), Tournoi (#tournament-link), Paramètres (#settings-link)
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

    // 4. Liste d'amis -> .friend-btn
    //    e.target.closest('.friend-btn') => ouvre un popup
    const friendButton = e.target.closest('.friend-btn');
    if (friendButton) {
        showFriendPopup(e, friendButton.innerText.trim());
        return;
    }

    // 5. Invitations d'amis (#friend-requests-list-container) -> bouton[data-request-id]
    //    on récupère l'ID et l'action (accepter/refuser)
    const friendRequestButton = e.target.closest('#friend-requests-list-container button[data-request-id]');
    if (friendRequestButton) {
        const requestId = friendRequestButton.getAttribute('data-request-id');
        const action = friendRequestButton.getAttribute('data-action');
        if (requestId) {
            handleFriendInvitation(requestId, action);
        }
        return;
    }

    // 6. Invitations de jeu (#game-invitations-list-container) -> bouton[data-invitation-id]
    const gameInvitationButton = e.target.closest('#game-invitations-list-container button[data-invitation-id]');
    if (gameInvitationButton) {
        const invitationId = gameInvitationButton.getAttribute('data-invitation-id');
        const action = gameInvitationButton.getAttribute('data-action');
        if (invitationId && action) {
            acceptGameInvitation(invitationId, action);
        }
        return;
    }

    // 7. Boutons du popup d'ami (voir profil, inviter à jouer, supprimer) => #view-profile-btn, #invite-to-play-btn, #remove-friend-btn
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

    // 8. Bouton de déconnexion (#logout-btn)
    if (e.target.matches('#logout-btn')) {
        e.preventDefault();
        handleLogout();
        return;
    }

    // Si aucun des cas ci-dessus n'est matché, on ne fait rien de particulier.
    // console.log("Clic dans burger-menu-container, mais cible non gérée:", e.target);
}
