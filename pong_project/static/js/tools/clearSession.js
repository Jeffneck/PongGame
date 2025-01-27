import { navigateTo } from '../router.js'; // Importer la fonction pour naviguer


/**
 * Supprime les tokens, nettoie l'interface utilisateur et redirige vers une URL donnée.
 * @param {string} redirectUrl - L'URL vers laquelle rediriger après le nettoyage. (Par défaut : '#core-home')
 */
export function clearSessionAndUI(redirectUrl = '/') {
    console.log('Nettoyage de la session et de l\'interface utilisateur...');

    // Suppression des tokens
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');

    // Nettoyage de l'interface utilisateur
    const navbar = document.querySelector('#navbar');
    const burgerMenu = document.querySelector('#burger-menu');
    const content = document.querySelector('#content');

    if (navbar) navbar.innerHTML = '';
    if (burgerMenu) burgerMenu.innerHTML = '';
    if (content) content.innerHTML = '';

    // Redirection
    navigateTo(redirectUrl);

    console.log(`Redirection vers ${redirectUrl}`);
}
