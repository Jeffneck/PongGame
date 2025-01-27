//utility.js
//fonctions que l' on ne sait pas encore ou mettre mais qui sont en rapport avec le jeu sur tel(loading screen)

export function isTouchDevice() {
    return 'ontouchstart' in window || navigator.maxTouchPoints > 0 || navigator.msMaxTouchPoints > 0;
}

export function resetScrollPosition() {
    window.scrollTo(0, 0);
}