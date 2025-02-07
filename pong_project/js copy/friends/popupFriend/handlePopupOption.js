import {  handleRemoveFriend } from '../index.js';
import { navigateTo } from '../../router.js';

export function handleOptionPopup(option) {
    console.log('Option popup cliquée' + option);
    const friendName = document.getElementById('popupFriendName').innerText.trim();
    console.log(`Option: ${option}, Friend: ${friendName}`); // Ajout de log

    if (option === 'Voir le profil') {
        const encodedName = encodeURIComponent(friendName);
        console.log(`Encoded friendName: ${encodedName}`);
        navigateTo(`/profile/${encodedName}`);
    } 
    else if (option === 'Inviter à jouer') {

        console.log(`Option sélectionnée : ${option}`);
    }
    else if (option === 'Supprimer') {
        handleRemoveFriend(friendName);
    }
    else {
        console.error(`Option inconnue : ${option}`);
    }
}
