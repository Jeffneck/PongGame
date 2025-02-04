// Fonction pour changer la viewBox du SVG
function updateSvgViewBox(mediaQuery) {
const svg = document.getElementById('eclair-svg');
console.log("svg passe ! ");
if (mediaQuery.matches) {
	// Condition pour le media query
	svg.setAttribute('viewBox', '150 -50 400 1350'); // Nouvelle viewBox pour petit écran
} else {
	// Condition par défaut
	svg.setAttribute('viewBox', '40 -20 650 1300'); // ViewBox originale
}
}

// Fonction pour changer la taille (width et height) du SVG
function updateSvgSize(mediaQuery) {
const svg = document.getElementById('eclair-svg');

if (mediaQuery.matches) {
	// Condition pour le media query
	svg.setAttribute('width', '30vh'); // Largeur ajustée pour petit écran
	svg.setAttribute('height', '100vw'); // Hauteur ajustée pour petit écran
} else {
	// Condition par défaut
	svg.setAttribute('width', '30vw'); // Largeur originale
	svg.setAttribute('height', '90vh'); // Hauteur originale
}
}

// Créez une media query
const mediaQuery = window.matchMedia("(max-aspect-ratio: 3/3)");

// Fonction principale pour mettre à jour le SVG
function updateSvg(mediaQuery) {
updateSvgViewBox(mediaQuery); // Mise à jour de la viewBox
updateSvgSize(mediaQuery);    // Mise à jour des dimensions
}
export async function TournamentNextMatch(){
// Ajoutez un écouteur d'événements pour les changements de media query
mediaQuery.addEventListener('change', () => updateSvg(mediaQuery));

// Appelez la fonction pour initialiser la bonne viewBox et taille
updateSvg(mediaQuery);

}