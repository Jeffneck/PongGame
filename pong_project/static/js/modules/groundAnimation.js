"use strict";
const terrainConfig = { width: 80, height: 40 };
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
const transitionTime = 2200;
let currentFrame = 0;
let animationRunning = true;
const balle = document.querySelector('.balle');
const traitGauche = document.querySelector('.trait-gauche');
const traitDroit = document.querySelector('.trait-droit');

function initPositions() {
  setPositions(frames[0]);
}

function setPositions(frame) {
  if (balle && traitGauche && traitDroit) {
    balle.style.left = frame.balleX + '%';
    balle.style.top = frame.balleY + '%';
    traitGauche.style.top = frame.raquetteGaucheY + '%';
    traitDroit.style.top = frame.raquetteDroiteY + '%';
  }
}

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

function updatePositions(frameActuelle, prochaineFrame, progress) {
  if (balle && traitGauche && traitDroit) {
    balle.style.left = interpolate(frameActuelle.balleX, prochaineFrame.balleX, progress) + '%';
    balle.style.top = interpolate(frameActuelle.balleY, prochaineFrame.balleY, progress) + '%';
    traitGauche.style.top = interpolate(frameActuelle.raquetteGaucheY, prochaineFrame.raquetteGaucheY, progress) + '%';
    traitDroit.style.top = interpolate(frameActuelle.raquetteDroiteY, prochaineFrame.raquetteDroiteY, progress) + '%';
  }
}

function interpolate(start, end, progress) {
  return start + (end - start) * progress;
}

export function stopPongAnimation() {
  animationRunning = false;
}

export async function loadPongAnimation() {
  initPositions();
  deplacerBalleEtRaquettes();
}
