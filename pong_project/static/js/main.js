// main.js

// Import des modules transverses
import { handleNavbar } from './navbar/index.js';
import { loadPongAnimation } from './modules/groundAnimation.js';
import { adjustBurgerHeight } from './modules/animations.js';
import { adjustSinNavHeight } from './modules/animations.js';
import { adjustContainerIfExists } from './modules/animations.js';
import { adjustAllContainers } from './modules/animations.js';
import { initializeRouter } from './router.js'; // Nouveau routeur Navigo

document.addEventListener('DOMContentLoaded', async () => {
    // Charger la navbar
    console.log('DOMContentLoaded');
    await handleNavbar();

    // Initialiser le routeur Navigo
    initializeRouter();

    // Charger les animations et ajustements au démarrage
    loadPongAnimation();
    adjustAllContainers(); // Pour resize
    adjustBurgerHeight(); // Pour load
    adjustSinNavHeight(); // Pour load
    adjustContainerIfExists('login'); // Pour load
    adjustContainerIfExists('register'); // Pour load
});