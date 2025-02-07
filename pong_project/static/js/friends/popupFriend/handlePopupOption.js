"use strict";
import { handleRemoveFriend } from '../index.js';
import { navigateTo } from '../../router.js';

export function handleOptionPopup(option) {
  const friendName = document.getElementById('popupFriendName').innerText.trim();
  if (option === 'Voir le profil') {
    const encodedName = encodeURIComponent(friendName);
    navigateTo(`/profile/${encodedName}`);
  } else if (option === 'Inviter à jouer') {
    // Ajoutez ici la logique pour inviter à jouer
    console.debug("Inviter à jouer pour", friendName);
  } else if (option === 'Supprimer') {
    handleRemoveFriend(friendName);
  } else {
    console.error(`Option inconnue : ${option}`);
  }
}
