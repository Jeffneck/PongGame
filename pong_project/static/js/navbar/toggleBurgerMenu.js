"use strict";
export function toggleBurgerMenu(flag) {
  console.debug('toggleBurgerMenu appelé');
  const menu = document.getElementById('burger-menu');
  const overlay = document.getElementById('overlay');
  if (flag === 'refresh btn') return;
  if (!menu || !overlay) return;
  if (menu.style.display === 'block') {
    closeBurgerMenu(menu, overlay);
  } else {
    openBurgerMenu(menu, overlay);
  }
}

function openBurgerMenu(menu, overlay) {
  menu.style.display = 'block';
  overlay.style.display = 'block';
}

function closeBurgerMenu(menu, overlay) {
  menu.style.display = 'none';
  overlay.style.display = 'none';
}
