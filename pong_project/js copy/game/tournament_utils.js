function updateSvgViewBox(mediaQuery) {
    const svg = document.getElementById('eclair-svg');
    if (!svg) {
        console.warn("L'élément 'eclair-svg' est introuvable dans le DOM.");
        return; // Arrête la fonction si l'élément n'existe pas
    }
    
    console.log("svg passe !");
    if (mediaQuery.matches) {
        svg.setAttribute('viewBox', '150 -50 400 1350'); // Pour petit écran
    } else {
        svg.setAttribute('viewBox', '40 -20 650 1300'); // ViewBox originale
    }
}
// Fonction pour changer la taille (width et height) du SVG
 // Fonction pour changer la taille (width et height) du SVG
 function updateSvgSize(mediaQuery) {
	const svg = document.getElementById('eclair-svg');
	if (!svg) {
		console.warn("L'élément 'eclair-svg' est introuvable dans le DOM.");
		return;
	}
	if (mediaQuery.matches) {
		svg.setAttribute('width', '30vh'); // Ajustée pour petit écran
		svg.setAttribute('height', '100vw');
	} else {
		svg.setAttribute('width', '30vw'); // Taille originale
		svg.setAttribute('height', '90vh');
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

