/**
 * Affiche un message de succès dans un élément spécifié.
 * @param {string} elementId - L'ID de l'élément où afficher le message.
 * @param {string} message - Le message de succès à afficher.
 */
export function displaySuccessMessage(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
        element.style.color = 'green';
        element.style.display = 'block';
    } else {
        console.warn(`Element with ID '${elementId}' not found.`);
    }
}

/**
 * Affiche un message d'erreur dans un élément spécifié.
 * @param {string} elementId - L'ID de l'élément où afficher le message.
 * @param {string} message - Le message d'erreur à afficher.
 */
export function displayErrorMessage(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
        element.style.color = 'red';
        element.style.display = 'block';
    } else {
        console.warn(`Element with ID '${elementId}' not found.`);
    }
}

/**
 * Affiche un message d'information dans un élément spécifié.
 * @param {string} elementId - L'ID de l'élément où afficher le message.
 * @param {string} message - Le message d'information à afficher.
 */
export function displayInfoMessage(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
        element.style.color = 'blue';
        element.style.display = 'block';
    } else {
        console.warn(`Element with ID '${elementId}' not found.`);
    }
}

/**
 * Efface les messages affichés dans un élément spécifié.
 * @param {string} elementId - L'ID de l'élément dont le contenu doit être effacé.
 */
export function clearMessage(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = '';
        element.style.display = 'none';
    } else {
        console.warn(`Element with ID '${elementId}' not found.`);
    }
}

export function showStatusMessage (message, status) {
    const popup = document.getElementById('popup');
    const info = document.getElementById('info');

    // Définir le message
    info.textContent = message;

    // Supprimer les anciennes classes
    popup.classList.remove('success', 'error', 'd-none', 'hide');

    // Ajouter la classe appropriée
    if (status === 'success') {
        popup.classList.add('success');
    } else if (status === 'error') {
        popup.classList.add('error');
    }

    // Afficher le popup
    popup.classList.add('show');

    // Cacher automatiquement après 3 secondes
    setTimeout(() => {
        popup.classList.remove('show');
        popup.classList.add('hide');
        setTimeout(() => popup.classList.add('d-none'), 500);
    }, 3000);
}