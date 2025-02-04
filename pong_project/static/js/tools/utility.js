//utility.js
//fonctions que l' on ne sait pas encore ou mettre mais qui sont en rapport avec le jeu sur tel(loading screen)


export function isTouchDevice() {
    return 'ontouchstart' in window || navigator.maxTouchPoints > 0 || navigator.msMaxTouchPoints > 0;
}

export function resetScrollPosition() {
    // document.scrollingElement est supporté par la majorité des navigateurs modernes.
    console.log("resetScrollPosition");
    const scrollingElement = document.scrollingElement || document.documentElement;
    scrollingElement.scrollTop = 0;
  }