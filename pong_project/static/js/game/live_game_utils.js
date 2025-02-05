function handleresizeTactile() {
	console.log(" It' s Device handleresizeTactile");
    // Dimensions internes du canvas (logique du jeu inchangée)
    const ORIGINAL_WIDTH = 800;   // Utilisé pour la hauteur du terrain (après rotation)
    const ORIGINAL_HEIGHT = 400;  // Utilisé pour la largeur du terrain (après rotation)
    const margin = 20;            // Marge interne dans la game-container
    const horizontalExtra = 2 * margin; // 40px au total
    const baseControlHeight = 100; // Hauteur de base des boutons pour s = 1

    // Pour le calcul vertical total, on tient compte de :
    // - La hauteur affichée du terrain : ORIGINAL_WIDTH * s + horizontalExtra
    // - La hauteur du conteneur des boutons : baseControlHeight * s
    // - Le padding vertical du conteneur principal (#livegame) : 20 top + 20 bottom = 40
    // - Une marge fixe entre terrain et boutons : 5px
    // Total vertical = 800*s + 40 + 100*s + 45 = 900*s + 85
    const verticalExtra = 85;

    // Pour le calcul horizontal, nous utilisons la largeur disponible dans la colonne Bootstrap.
    const parentCol = document.getElementById('game-col');
    const availableWidth = parentCol ? parentCol.clientWidth : window.innerWidth;

    // Calcul de l'échelle horizontal : la largeur affichée du terrain sera ORIGINAL_HEIGHT * s + horizontalExtra
    const s_h = (availableWidth - horizontalExtra) / ORIGINAL_HEIGHT;

    // Calcul de l'échelle vertical : l'espace total requis verticalement est 900*s + 85, qui doit tenir dans window.innerHeight.
    const s_v = (window.innerHeight - verticalExtra) / 900;

    // On prend le facteur le plus contraignant
    const computedS = Math.min(s_h, s_v);

    // Calcul de l'échelle minimale pour que le terrain ait au moins 100px de largeur et 200px de hauteur.
    const sMinWidth = (100 - horizontalExtra) / ORIGINAL_HEIGHT;   // (100 - 40)/400 = 0.15
    const sMinHeight = (200 - horizontalExtra) / ORIGINAL_WIDTH;    // (200 - 40)/800 = 0.2
    const sMin = Math.max(sMinWidth, sMinHeight); // ici sMin = 0.2

    // On s'assure que l'échelle ne descend pas en dessous de sMin.
    const s = Math.max(computedS, sMin);

    // Mise à jour des dimensions du game-container (terrain)
    const gameContainer = document.querySelector('.game-container');
    gameContainer.style.width = (ORIGINAL_HEIGHT * s + horizontalExtra) + "px"; // 400*s + 40
    gameContainer.style.height = (ORIGINAL_WIDTH * s + horizontalExtra) + "px";  // 800*s + 40

    // Transformation du canvas pour le rendre vertical :
    const canvas = document.getElementById('gameCanvas');
    canvas.style.transform =
      `translate(${margin}px, ${margin}px) translateY(${ORIGINAL_WIDTH * s}px) rotate(-90deg) scale(${s})`;

    // Mise à jour de la hauteur du conteneur des boutons (touch-controls) en fonction de l'échelle.
    const controls = document.getElementById('left_player');
    const controlHeight = baseControlHeight * s;
    if (controls) {
      controls.style.height = controlHeight + "px";
    }

    // Transmet l'échelle aux boutons via la variable CSS --btn-scale pour qu'ils se redimensionnent proportionnellement.
    document.documentElement.style.setProperty('--btn-scale', s);

    // Mise à jour de la position de la zone de score pour l'accrocher entre le bord du game-container et celui du canvas (sans rotation)
const scoreDisplay = document.getElementById("score-display");
if (scoreDisplay) {
    // On souhaite que le score soit positionné de sorte que son centre soit à mi-distance
    // entre le bord gauche du game-container (0) et le bord gauche du canvas (qui est à "margin" pixels)
    const posX = margin / 2;  // Ceci correspond au point milieu horizontal
    // Pour le centrage vertical, on se base sur la hauteur actuelle du game-container.
    const posY = gameContainer.clientHeight / 2;
    
    // Positionnement absolu dans le game-container :
    scoreDisplay.style.left = posX + "px";
    scoreDisplay.style.top = posY + "px";
    
    // Appliquer un translate(-50%, -50%) pour que le centre de la zone corresponde à ce point,
    // sans aucune rotation (le texte reste dans son orientation normale)
    scoreDisplay.style.transform = "translate(-50%, -50%)";
    scoreDisplay.style.transformOrigin = "center";
    
    // Adaptez la taille de la police en fonction du scale, pour qu'elle reste proportionnelle
    scoreDisplay.style.fontSize = (1.5 * s) + "rem";
}

}

  
  

  



function handleResize() {
	console.log("not device handlerize");
    const ORIGINAL_WIDTH = 800;
    const ORIGINAL_HEIGHT = 400;
	const canvas = document.getElementById('gameCanvas');
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
