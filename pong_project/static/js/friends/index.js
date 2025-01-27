
// Fonction qui permet de gérer les actions liées aux amis
export { handleAddFriend } from "./friendsAction/addFriend.js";
export { handleFriendProfile } from "./friendsAction/friendProfile.js";
export { handleFriendInvitation } from "./friendsAction/friendsInvitations.js";
export { handleRemoveFriend } from "./friendsAction/removeFriend.js";

// Fonction qui permet de gérer les événements liés au popup de la liste d'amis
export { handleOptionPopup } from "./popupFriend/handlePopupOption.js";

// Fonction qui permet de gérer la mécanique du popup de la liste d'amis
export { showFriendPopup, closePopupOnClickOutside  } from "./popupFriend/popupMechanics.js";


