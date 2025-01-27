// Ajuster la hauteur du menu burger avec marges
export function adjustBurgerHeight() {
    const navAndMarginHeight = 66; // Hauteur navbar et marge pour le menu burger
    const availableHeight = window.innerHeight - navAndMarginHeight;
    document.documentElement.style.setProperty('--burger-height', `${availableHeight}px`);
}

// Ajuster la hauteur sans la barre navigation
export function adjustSinNavHeight() {
    const navAndMarginHeight = 50; // Hauteur sans la navbar
    const availableHeight = window.innerHeight - navAndMarginHeight;
    document.documentElement.style.setProperty('--sin-nav-height', `${availableHeight}px`);
}


//Fonction responsive
function adjustContainer(ContainerId) {
  console.log("Rentre dans adjust container");
	const container = document.getElementById(ContainerId);
	if (!container) {
    console.log("adjustContainer: container error");
    return;
  } 
	const threshold = 50; // Seuil de hauteur pour activer le centrage
	// Si le contenu dépasse la hauteur de l'écran, on enlève `center-content`
	if (container.scrollHeight > window.innerHeight - threshold) {
		container.classList.remove('center-content');
		container.classList.add('normal-content');
	} else {
    container.classList.add('center-content');
		container.classList.remove('normal-content');
	}
}


/**
 * Vérifie si un élément avec l'ID spécifié existe dans le DOM
 * et appelle adjustContainer si l'élément est présent.
 * @param {string} containerId - L'ID de l'élément à ajuster.
 */
export function adjustContainerIfExists(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        adjustContainer(containerId);
    }
}


//[IMPROVE] Faire en sorte que adjustContainer login et register soit bind en event uniquement au chargement de leurs pages respectives pour éviter de les appeler inutilement

export function adjustAllContainers() {

    window.addEventListener('resize', () => {
        adjustBurgerHeight();
        adjustSinNavHeight();
        adjustContainerIfExists('login');
        adjustContainerIfExists('register');

    });
}
