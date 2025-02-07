// Configuration et données des frames
const terrainConfig = {
	width: 80, // en pourcentage (vw)
	height: 40 // en pourcentage (vh)
  };
  
  const frames = [
	{ balleX: 1, balleY: 47, raquetteGaucheY: 36.5, raquetteDroiteY: 36.5 },
	{ balleX: 48, balleY: 0, raquetteGaucheY: 0, raquetteDroiteY: 73 },
	{ balleX: 97, balleY: 47, raquetteGaucheY: 47, raquetteDroiteY: 26 },
	{ balleX: 41, balleY: 95, raquetteGaucheY: 7, raquetteDroiteY: 69 },
	{ balleX: 1, balleY: 60, raquetteGaucheY: 60, raquetteDroiteY: 10 },
	{ balleX: 53, balleY: 0, raquetteGaucheY: 7, raquetteDroiteY: 65 },
	{ balleX: 97, balleY: 37, raquetteGaucheY: 67, raquetteDroiteY: 32 },
	{ balleX: 48, balleY: 95, raquetteGaucheY: 7, raquetteDroiteY: 73 }
  ];
  
  const transitionTime = 2200; // Temps de transition en ms
  let currentFrame = 0;
  let animationRunning = true;
  
  // Sélection des éléments
  const balle = document.querySelector('.balle');
  const traitGauche = document.querySelector('.trait-gauche');
  const traitDroit = document.querySelector('.trait-droit');
  
  /**
   * Initialise les positions des éléments (balle, raquettes) à partir de la première frame.
   */
  function initPositions() {
	setPositions(frames[0]);
  }
  
  /**
   * Met à jour les positions des éléments en fonction de la frame donnée.
   * @param {Object} frame - Frame contenant les positions de la balle et des raquettes.
   */
  function setPositions(frame) {
	balle.style.left = frame.balleX + '%';
	balle.style.top = frame.balleY + '%';
	traitGauche.style.top = frame.raquetteGaucheY + '%';
	traitDroit.style.top = frame.raquetteDroiteY + '%';
  }
  
  /**
   * Déplace la balle et les raquettes avec interpolation entre les frames.
   */
  function deplacerBalleEtRaquettes() {
	if (!animationRunning) return;
  
	const frameActuelle = frames[currentFrame];
	const prochaineFrame = frames[(currentFrame + 1) % frames.length];
	let startTime = null;
  
	function animate(time) {
	  if (!animationRunning) return;
  
	  if (!startTime) startTime = time;
	  const progress = (time - startTime) / transitionTime;
  
	  if (progress < 1) {
		updatePositions(frameActuelle, prochaineFrame, progress);
		requestAnimationFrame(animate);
	  } else {
		currentFrame = (currentFrame + 1) % frames.length;
		requestAnimationFrame(deplacerBalleEtRaquettes);
	  }
	}
  
	requestAnimationFrame(animate);
  }
  
  /**
   * Met à jour les positions interpolées de la balle et des raquettes.
   * @param {Object} frameActuelle - Frame actuelle.
   * @param {Object} prochaineFrame - Frame suivante.
   * @param {number} progress - Progression de l'interpolation (de 0 à 1).
   */
  function updatePositions(frameActuelle, prochaineFrame, progress) {
	balle.style.left = interpolate(frameActuelle.balleX, prochaineFrame.balleX, progress) + '%';
	balle.style.top = interpolate(frameActuelle.balleY, prochaineFrame.balleY, progress) + '%';
	traitGauche.style.top = interpolate(frameActuelle.raquetteGaucheY, prochaineFrame.raquetteGaucheY, progress) + '%';
	traitDroit.style.top = interpolate(frameActuelle.raquetteDroiteY, prochaineFrame.raquetteDroiteY, progress) + '%';
  }
  
  /**
   * Fonction d'interpolation linéaire.
   * @param {number} start - Valeur de départ.
   * @param {number} end - Valeur d'arrivée.
   * @param {number} progress - Progression entre 0 et 1.
   * @returns {number} - Valeur interpolée.
   */
  function interpolate(start, end, progress) {
	return start + (end - start) * progress;
  }
  
/**
 * Arrête l'animation.
 */
export function stopPongAnimation() {
  animationRunning = false;
  }
  

export async function loadPongAnimation() {
    // Initialisation et lancement
    initPositions();
    deplacerBalleEtRaquettes();
  }
