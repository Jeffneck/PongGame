import { showFriendPopup, closePopupOnClickOutside, handleOptionPopup,  handleAddFriend, handleFriendInvitation  } from '../friends/index.js';
import { handleStatusChange } from './index.js';
import { handleLogout } from '../auth/index.js';
import { navigateTo } from '../router.js';
import { handleGameInvitationBurgerMenu } from '../game/index.js';
// Gestionnaire principal des événements pour le menu burger
export function eventsHandlerBurgerMenu() {
    console.log('Initialisation des gestionnaires d\'événements...');

    // Initialise les événements spécifiques au menu burger
    setupStatusChangeEvents();  // Gestion du changement de statut (en ligne/hors ligne)
    setupProfileViewEvent();    // Gestion du clic sur le bouton "Voir le profil"
    setupNavigationEvents();    // Gestion des boutons de navigation (Jouer, Tournoi, Paramètres)
    setupAddFriendEvent();      // Gestion du formulaire d'ajout d'ami
    setupFriendsListEvent();    // Gestion des clics sur les amis dans la liste
    setupFriendRequestsEvent(); // Gestion des invitations d'amis
    setupGameInvitationsEvent();
    setupPopupEvents();         // Gestion des options du popup d'ami
    setupLogoutEvent();         // Gestion du bouton de déconnexion
    setupClosePopupEvent();     // Gestion de la fermeture du popup

    console.log('Tous les gestionnaires d\'événements ont été initialisés.');
}

// Gestion des boutons pour changer le statut (en ligne/hors ligne)
function setupStatusChangeEvents() {
    document.querySelectorAll('.status-selector button[data-status]').forEach(button => {
        if (!button.dataset.bound) {  // Vérifie si l'événement est déjà attaché
            button.addEventListener('click', handleStatusChangeWrapper);
            button.dataset.bound = true; // Marque comme attaché pour éviter les doublons
        }
    });
}

// Wrapper pour gérer le changement de statut
function handleStatusChangeWrapper(e) {
    const status = e.target.dataset.status;
    if (status) handleStatusChange(status);
}


// Gestion du clic sur "Voir le profil"
function setupProfileViewEvent() {
    const profileBtn = document.querySelector('#profile-btn');
    if (profileBtn && !profileBtn.dataset.bound) {
        profileBtn.addEventListener('click', (event) => {
            event.preventDefault(); // Empêche le comportement par défaut du lien
            console.log('Profil bouton cliqué');
            navigateTo('/profile'); // Navigue vers la route profil
        });
        profileBtn.dataset.bound = true; // Marque comme attaché pour éviter les doublons
    }
}

// Gestion des boutons de navigation (Jouer, Tournoi, Paramètres)
function setupNavigationEvents() {
    const navigationButtons = [
        { selector: '#play-btn', action: () => navigateTo('/game-options') },
        { selector: '#tournament-link', action: () => navigateTo('/select_tournament')},
        { selector: '#settings-link', action: () => navigateTo('/account')},
    ];

    navigationButtons.forEach(nav => {
        const button = document.querySelector(nav.selector);
        if (button && !button.dataset.bound) {
            console.log('bouton trouvé :', button);
            button.addEventListener('click', (e) => {
                e.preventDefault();
                nav.action();
            });
            button.dataset.bound = true;
        }
    });
}

// Gestion du formulaire d'ajout d'ami
function setupAddFriendEvent() {
    const addFriendForm = document.querySelector('#add-friend-form');
    console.log('ajout d\'ami :', addFriendForm);
    if (addFriendForm && !addFriendForm.dataset.bound) {
        addFriendForm.addEventListener('submit', handleAddFriend);
        addFriendForm.dataset.bound = true;
    }
}

// Gestion des clics sur les amis dans la liste
function setupFriendsListEvent() {
    const friendsListContainer = document.querySelector('#friends-list-container');
    if (friendsListContainer && !friendsListContainer.dataset.bound) {
        friendsListContainer.addEventListener('click', (e) => {
            const friendButton = e.target.closest('.friend-btn');
            if (friendButton) showFriendPopup(e, friendButton.innerText.trim());
        });
        friendsListContainer.dataset.bound = true;
    }
}

// Gestion des clics sur les invitations d'amis
function setupFriendRequestsEvent() {
    const friendRequestsContainer = document.querySelector('#friend-requests-list-container');
    if (friendRequestsContainer && !friendRequestsContainer.dataset.bound) {
        friendRequestsContainer.addEventListener('click', async (e) => {
            const button = e.target.closest('button');
            if (button) {
                const requestId = button.getAttribute('data-request-id');
                const action = button.getAttribute('data-action');
                if (requestId) await handleFriendInvitation(requestId, action);
            }
        });
        friendRequestsContainer.dataset.bound = true;
    }
}

// Gestion des clics sur les invitations à jouer
function setupGameInvitationsEvent() {
    const gameInvitationsContainer = document.querySelector('#game-invitations-list-container');
    if (gameInvitationsContainer && !gameInvitationsContainer.dataset.bound) {
        gameInvitationsContainer.addEventListener('click', async (e) => {
            const button = e.target.closest('button');
            if (button) {
                const invitationId = button.getAttribute('data-invitation-id');
                const action = button.getAttribute('data-action');
                if (invitationId && action) {
                    await handleGameInvitationBurgerMenu(invitationId, action);
                }
            }
        });
        gameInvitationsContainer.dataset.bound = true;
    }
}

// Gestion des événements du popup d'ami (Voir profil, Inviter à jouer, Supprimer)
function setupPopupEvents() {
    const viewProfileBtn = document.getElementById('view-profile-btn');
    const inviteToPlayBtn = document.getElementById('invite-to-play-btn');
    const removeFriendBtn = document.getElementById('remove-friend-btn');

    if (viewProfileBtn && !viewProfileBtn.dataset.bound) {
        viewProfileBtn.addEventListener('click', () => handleOptionPopup('Voir le profil'));
        viewProfileBtn.dataset.bound = true;
    }

    if (inviteToPlayBtn && !inviteToPlayBtn.dataset.bound) {
        inviteToPlayBtn.addEventListener('click', () => handleOptionPopup('Inviter à jouer'));
        inviteToPlayBtn.dataset.bound = true;
    }

    if (removeFriendBtn && !removeFriendBtn.dataset.bound) {
        removeFriendBtn.addEventListener('click', () => handleOptionPopup('Supprimer'));
        removeFriendBtn.dataset.bound = true;
    }
}

// Gestion du bouton de déconnexion
function setupLogoutEvent() {
    const logoutButton = document.querySelector('#logout-btn');
    if (logoutButton && !logoutButton.dataset.bound) {
        logoutButton.addEventListener('click', async (e) => {
            e.preventDefault();
            await handleLogout();
        });
        logoutButton.dataset.bound = true;
    }
}

// Gestion de la fermeture du popup d'ami en cliquant en dehors
function setupClosePopupEvent() {
    const popup = document.getElementById('friendPopup');
    if (popup && !popup.dataset.bound) {
        document.addEventListener('click', closePopupOnClickOutside);
        popup.dataset.bound = true;
    }
}

