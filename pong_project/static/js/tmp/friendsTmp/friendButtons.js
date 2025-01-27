// friends/friendButtons.js
//fonctions actuellement inutilisees dans le code

// Gère l'initialisation des boutons amis et l'affichage du popup.

export function initializeFriendButtons() {
    $('.friend-btn').off('click').on('click', function(event) {
        const friendName = $(this).data('username');
        showFriendPopup(event, friendName);
    });
}

// Si showFriendPopup est ailleurs, importez-la, sinon définissez-la ici :
export function showFriendPopup(event, friendName) {
    // Logique d'affichage du popup ami
    console.log(`Affichage du popup pour l'ami: ${friendName}`);
    // TODO: Implémentez l’affichage du popup selon votre code HTML/CSS
}
