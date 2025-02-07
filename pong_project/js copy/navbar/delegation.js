// burgerMenu/delegation.js

/**
 * Initialise la délégation d'événements pour gérer la fermeture du burger menu.
 */
export function initBurgerMenuDelegation() {
    // Gestion du clic extérieur pour fermer le menu
    document.addEventListener('click', (event) => {
        const menu = document.getElementById('burger-menu');
        const burgerToggle = document.getElementById('burger-menu-toggle');
        const overlay = document.getElementById('overlay');
        if (!menu || !burgerToggle || !overlay) return;

        // Si le menu est affiché et que le clic se fait en dehors du menu et du toggle...
        if (
            menu.style.display === 'block' &&
            !menu.contains(event.target) &&
            !burgerToggle.contains(event.target)
        ) {
            menu.style.display = 'none';
            overlay.style.display = 'none';
        }
    });

    // Gestion déléguée pour les boutons qui ferment le burger menu
    document.addEventListener('click', (event) => {
        if (event.target.matches('#profile-btn, #play-btn, #settings-link, #view-profile-btn')) {
            const menu = document.getElementById('burger-menu');
            const overlay = document.getElementById('overlay');
            if (menu && overlay) {
                menu.style.display = 'none';
                overlay.style.display = 'none';
            }
        }
    });
}
