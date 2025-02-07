"use strict";
export function initBurgerMenuDelegation() {
  document.addEventListener('click', (event) => {
    const menu = document.getElementById('burger-menu');
    const burgerToggle = document.getElementById('burger-menu-toggle');
    const overlay = document.getElementById('overlay');
    if (!menu || !burgerToggle || !overlay) return;
    if (menu.style.display === 'block' && !menu.contains(event.target) && !burgerToggle.contains(event.target)) {
      menu.style.display = 'none';
      overlay.style.display = 'none';
    }
  });
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
