// Utilitaire pour mettre à jour le contenu texte d'un élément HTML
/**
 * Met à jour le texte affiché d'un élément HTML sélectionné.
 *
 * @param {string} selector - Sélecteur CSS pour cibler l'élément HTML.
 * @param {string} text - Contenu texte à insérer dans l'élément.
 *
 * Cette fonction utilise `querySelector` pour sélectionner **le premier élément**
 * correspondant au sélecteur fourni.
 * 
 * - Si le sélecteur est une **classe combinée** comme `.profile-info h3`, la fonction
 *   va chercher **le premier `<h3>`** trouvé à l'intérieur de l'élément ayant la classe `profile-info`.
 * - Si l'élément a un **`id` unique** (ex. : `id="profile-username"`), vous pouvez le cibler directement
 *   avec le sélecteur `#profile-username`, ce qui est plus précis et performant.
 *
 * Si l'élément correspondant n'est pas trouvé dans le DOM, la fonction ne fait rien
 * et ne lève aucune erreur.
 *
 * Exemple d'utilisation avec une classe combinée :
 * updateTextContent('.profile-info h3', 'Pseudo : JohnDoe');
 *
 * Exemple d'utilisation avec un `id` :
 * updateTextContent('#profile-username', 'Pseudo : JohnDoe');
 *
 * Résultat attendu dans le DOM :
 * Avant : <h3 class="profile-info">Pseudo :</h3>
 * Après : <h3 class="profile-info">Pseudo : JohnDoe</h3>
 */
export function updateTextContent(selector, text) {
    const element = document.querySelector(selector); // Sélectionne le premier élément correspondant au sélecteur
    if (element) {
        element.textContent = text; // Modifie le contenu texte de l'élément
    }
}

// Utilitaire pour mettre à jour un attribut d'un élément HTML
/**
 * Met à jour un attribut spécifique d'un élément HTML sélectionné.
 *
 * @param {string} selector - Sélecteur CSS pour cibler l'élément HTML.
 * @param {string} attribute - Nom de l'attribut à mettre à jour (par ex. : `src`, `alt`, `href`).
 * @param {string} value - Nouvelle valeur à attribuer à l'attribut.
 *
 * Cette fonction utilise `querySelector` pour sélectionner **le premier élément**
 * correspondant au sélecteur fourni.
 * 
 * - Si le sélecteur est une **classe combinée** comme `.profile-info img`, la fonction
 *   va chercher **la première balise `<img>`** trouvée à l'intérieur de l'élément ayant la classe `profile-info`.
 * - Si l'élément possède un **`id` unique**, il est recommandé d'utiliser ce `id` directement
 *   dans le sélecteur (ex. : `#profile-avatar`) pour une sélection plus rapide et précise.
 *
 * Si l'élément correspondant n'est pas trouvé dans le DOM, la fonction ne fait rien
 * et ne lève aucune erreur.
 *
 * Exemple d'utilisation avec une classe combinée :
 * updateAttribute('.profile-info img', 'src', '/path/to/image.jpg');
 *
 * Exemple d'utilisation avec un `id` :
 * updateAttribute('#profile-avatar', 'src', '/path/to/image.jpg');
 *
 * Résultat attendu dans le DOM :
 * Avant : <img class="profile-info" src="" alt="">
 * Après : <img class="profile-info" src="/path/to/image.jpg" alt="">
 */
export function updateAttribute(selector, attribute, value) {
    const element = document.querySelector(selector);
    console.log(`Sélecteur : ${selector}, Élément trouvé :`, element);
    if (element) {
        element.setAttribute(attribute, value);
        console.log(`Attribut ${attribute} mis à jour avec la valeur : ${value}`);
    } else {
        console.error(`Élément non trouvé pour le sélecteur : ${selector}`);
    }
}

//Ajout et modification dynamique du html dans les divs
// Selector = #content ou #navbar 
//  [IMPROVE] A voir aussi ou inclure le bruger menu 
export function updateHtmlContent(selector, html) {
    console.log(`rentre dans updateHtmlContent selector =`, selector);
    if (!html)
            console.log('html est vide');
    try {
        // Mise à jour du contenu à partir des données reçues
        document.querySelector(selector).innerHTML = html;
    } catch {
        //[IMPROVE] faire un autre throw ici pour gerer l' erreur dans les fonctions specialisees
        document.querySelector(selector).innerHTML = '<p>Une erreur est survenue lors du chargement du contenu.</p>';
    }
}

