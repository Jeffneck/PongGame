"use strict";
function updateSvgViewBox(mediaQuery) {
  const svg = document.getElementById('eclair-svg');
  if (!svg) {
    console.warn("L'élément 'eclair-svg' est introuvable.");
    return;
  }
  if (mediaQuery.matches) {
    svg.setAttribute('viewBox', '150 -50 400 1350');
  } else {
    svg.setAttribute('viewBox', '40 -20 650 1300');
  }
}

function updateSvgSize(mediaQuery) {
  const svg = document.getElementById('eclair-svg');
  if (!svg) {
    console.warn("L'élément 'eclair-svg' est introuvable.");
    return;
  }
  if (mediaQuery.matches) {
    svg.setAttribute('width', '30vh');
    svg.setAttribute('height', '100vw');
  } else {
    svg.setAttribute('width', '30vw');
    svg.setAttribute('height', '90vh');
  }
}

function updateSvg(mediaQuery) {
  updateSvgViewBox(mediaQuery);
  updateSvgSize(mediaQuery);
}

const mediaQuery = window.matchMedia("(max-aspect-ratio: 3/3)");

export async function TournamentNextMatch() {
  mediaQuery.addEventListener('change', () => updateSvg(mediaQuery));
  updateSvg(mediaQuery);
}
