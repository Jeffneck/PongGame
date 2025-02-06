// export function isTouchDevice() {
//   return (('ontouchstart' in window) || 
//           (navigator.maxTouchPoints && navigator.maxTouchPoints > 0) || 
//           (navigator.msMaxTouchPoints && navigator.msMaxTouchPoints > 0));
// }

  



function handleResize() {
    const ORIGINAL_WIDTH = 800;
    const ORIGINAL_HEIGHT = 400;
    const margin = 12; // Marge interne utilisée pour le positionnement
    const container = document.querySelector('.game-container');
	const containerHeight = container.clientHeight;
    if (!container) return;

    // Dimensions du conteneur et de la fenêtre
    const containerWidth = container.clientWidth;
    const windowHeight = window.innerHeight;

    // Calcul du scale en fonction de l'espace disponible
    let scale = Math.min(containerWidth / ORIGINAL_WIDTH, windowHeight * 0.7 / ORIGINAL_HEIGHT);

    // Appliquer le scale sur le canvas (dimension affichée)
    canvas.style.width = (ORIGINAL_WIDTH * scale) + 'px';
    canvas.style.height = (ORIGINAL_HEIGHT * scale) + 'px';

    // Garder la résolution logique du canvas inchangée
    canvas.width = ORIGINAL_WIDTH;
    canvas.height = ORIGINAL_HEIGHT;
    
    // Ajuster dynamiquement la hauteur du game-container (en fonction de la largeur)
    container.style.height = Math.min(windowHeight * 0.8, containerWidth / 2) + 'px';

    ctx.imageSmoothingEnabled = false;

    // Utilisation du facteur d'échelle pour d'autres ajustements
    const s = scale;

    // Positionnement absolu de score-display par rapport à game-container
    // On considère que :
    //   - Le canvas est positionné en absolute dans le game-container (déjà défini dans votre CSS).
    //   - Le canvas est décalé d'une marge (margin) par rapport au bord supérieur et gauche du container.
    // On positionne alors le score-display pour qu'il soit centré horizontalement sur le bord supérieur du canvas.
    const scoreDisplay = document.getElementById("score-display");
    if (scoreDisplay) {
        // Assurez-vous que le game-container est en position relative (pour que le positionnement absolu se fasse par rapport à lui)
        container.style.position = "relative";
        // Le canvas devrait être positionné en absolute (vérifiez votre CSS)
        // Récupérer la position du canvas par rapport au container (offsetLeft et offsetTop fonctionnent si le container est en position relative)
        const canvasLeft = canvas.offsetLeft;
        const canvasTop = canvas.offsetTop;
        // Calculer la largeur affichée du canvas (en pixels)
        const canvasDisplayWidth = ORIGINAL_WIDTH * s;

        // Placer le score-display centré sur le bord supérieur du canvas.
        // On fixe sa position verticale à la même valeur que canvasTop (souvent égale à la marge appliquée)
        // et sa position horizontale au centre du canvas.
        scoreDisplay.style.position = "absolute";
        scoreDisplay.style.left = (canvasLeft + canvasDisplayWidth / 2) + "px";
        scoreDisplay.style.top = (canvasTop + 2) + "px";
        // Pour centrer le score-display par rapport à son point de positionnement, on décale de 50% de sa largeur.
        scoreDisplay.style.transform = "translate(-50%, 0)";
        scoreDisplay.style.transformOrigin = "center top";

        // On fixe la taille de la police en pixels pour éviter les fluctuations liées aux unités rem
        scoreDisplay.style.fontSize = (30 * s) + "px";
    }
}

window.addEventListener('resize', handleResize);
handleResize(); // Appel initial


function updateScoreDisplay() {
	const scoreEl = document.getElementById("score-nb");
	if (scoreEl) {
	  // Ici, on suppose que les noms sont déjà injectés via Django dans le HTML.
	  // Par exemple, on pourrait avoir utilisé des attributs data pour conserver ces noms.
	  // Si ce n'est pas le cas, vous pouvez également définir des variables globales injectées par Django.
	  // Ici, nous allons lire le texte initial et remplacer uniquement la partie numérique.
	  // Pour plus de flexibilité, vous pouvez modifier cette fonction selon vos besoins.
	  // Exemple avec des attributs data (optionnel) :
	  scoreEl.innerText = ` ${gameState.score_left} - ${gameState.score_right} `;
	}
  }

  updateScoreDisplay();