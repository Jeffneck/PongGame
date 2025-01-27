import { HTTPError, ContentTypeError, NetworkError } from './apiErrors.js';

const Api = {
    /**
     * Effectue une requête HTTP avec fetch en utilisant FormData.
     * @param {string} url - L'URL complète de la ressource.
     * @param {string} method - La méthode HTTP (GET, POST, PUT, DELETE).
     * @param {FormData|null} formData - Les données à envoyer dans le corps de la requête, sous forme de FormData.
     * @param {Object} headers - Headers supplémentaires à ajouter.
     * @returns {Promise} - Une promesse résolue avec les données JSON ou rejetée en cas d'erreur.
     */
    async request(url, method = 'GET', formData = null, headers = {}) {
        const jwtAccessToken = this.getJWTaccessToken();

        // Vérifie si le token expire bientôt et le renouvelle si nécessaire
        if (jwtAccessToken && this.isTokenExpiringSoon(jwtAccessToken)) {
            console.warn('Access token sur le point d\'expirer, tentative de renouvellement...');
            await this.handleTokenRefresh();
        }

        const defaultHeaders = this.prepareHeaders();

        try {
            let response = await this.sendRequest(url, method, formData, { ...defaultHeaders, ...headers });

            // Gestion des erreurs HTTP non réussies
            if (!response.ok) {
                if (response.status === 401) {
                    response = await this.handleUnauthorized(url, method, formData, headers, defaultHeaders);
                } else {
                    throw new HTTPError(
                        response.statusText || 'Une erreur est survenue',
                        response.status
                    );
                }
            }

            return this.handleResponse(response); // Traite la réponse
        } catch (error) {
            if (error instanceof TypeError) {
                throw new NetworkError('Échec réseau : ' + error.message);
            }

            throw error;
        }
    },

    /**
     * Prépare les en-têtes pour la requête.
     * @returns {Object} - Les en-têtes préparés.
     */
    prepareHeaders() {
        const csrfToken = this.getCSRFToken();
        const jwtAccessToken = this.getJWTaccessToken();

        const headers = {
            'X-CSRFToken': csrfToken,
        };

        if (jwtAccessToken) {
            headers['Authorization'] = `Bearer ${jwtAccessToken}`;
        }

        return headers;
    },

    /**
     * Vérifie si le token expire bientôt.
     * @param {string} token - Le token JWT.
     * @returns {boolean} - True si le token expire dans moins de 5 minutes.
     */
    isTokenExpiringSoon(token) {
        try {
            const payload = JSON.parse(atob(token.split('.')[1])); // Décodage du payload JWT
            const currentTime = Math.floor(Date.now() / 1000); // Temps actuel en secondes
            const expiryTime = payload.exp;
            return expiryTime - currentTime < 300; // Expire dans moins de 5 minutes
        } catch (error) {
            console.error('Erreur lors de la vérification de l\'expiration du token :', error);
            return true; // Si une erreur survient, considérer le token comme expiré
        }
    },

    async sendRequest(url, method, formData, headers) {
        return fetch(url, {
            method,
            headers,
            body: (method !== 'GET' && formData instanceof FormData) ? formData : undefined,
        });
    },

    async handleUnauthorized(url, method, formData, headers, defaultHeaders) {
        console.warn('Access token expiré, tentative de rafraîchissement...');
        const newAccessToken = await this.handleTokenRefresh();

        if (newAccessToken) {
            // Met à jour les en-têtes avec le nouveau token
            defaultHeaders['Authorization'] = `Bearer ${newAccessToken}`;
            const response = await this.sendRequest(url, method, formData, { ...defaultHeaders, ...headers });

            // Vérifie de nouveau la réponse
            if (!response.ok) {
                throw new HTTPError(
                    response.statusText || 'Échec après rafraîchissement du token',
                    response.status
                );
            }

            return response; // Retourne la nouvelle réponse réussie
        } else {
            throw new HTTPError('Impossible de rafraîchir le token.', 401);
        }
    },

    async handleTokenRefresh() {
        const jwtRefreshToken = this.getJWTrefreshToken();

        if (!jwtRefreshToken) {
            console.error('Aucun refresh token disponible.');
            return null;
        }

        try {
            const csrfToken = this.getCSRFToken();
            const response = await fetch('/accounts/refreshJwt/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken, // Inclure le CSRF token
                },
                body: JSON.stringify({ refresh_token: jwtRefreshToken }),
            });

            if (response.ok) {
                const data = await response.json();
                const newAccessToken = data.access_token;

                // Met à jour l'access token dans le stockage local
                localStorage.setItem('access_token', newAccessToken);
                return newAccessToken;
            } else {
                console.error('Erreur lors du rafraîchissement du token :', response.statusText);
                return null;
            }
        } catch (error) {
            console.error('Échec du rafraîchissement du token :', error);
            return null;
        }
    },

    handleResponse(response) {
        const contentType = response.headers.get('Content-Type');
    
        if (response.ok && contentType && contentType.includes('application/json')) {
            return response.json();
        } else if (!response.ok && contentType && contentType.includes('application/json')) {
            // En cas d'erreur avec un JSON dans la réponse
            return response.json().then(errorData => {
                throw new HTTPError(errorData.message || 'Erreur inconnue.', response.status);
            });
        } else {
            // Erreur générique pour les autres types de réponses
            throw new HTTPError('Réponse inattendue.', response.status);
        }
    },

    getCSRFToken() {
        const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
        return cookie ? cookie.trim().substring('csrftoken='.length) : '';
    },

    getJWTaccessToken() {
        return localStorage.getItem('access_token') || null;
    },

    getJWTrefreshToken() {
        return localStorage.getItem('refresh_token') || null;
    },

    // Méthodes pour les requêtes HTTP spécifiques
    async get(url) {
        return await this.request(url, 'GET');
    },

    async post(url, formData) {
        return await this.request(url, 'POST', formData);
    },

    async put(url, formData) {
        return await this.request(url, 'PUT', formData);
    },

    async delete(url) {
        return await this.request(url, 'DELETE');
    }
};

// Fonctions appelables depuis les autres fichiers
export async function requestGet(app, view) {
    const url = `/${app}/${view}/`;

    try {
        return await Api.get(url);
    } catch (error) {
        console.error(`Erreur lors du chargement de ${app}-${view} :`, error);
        throw error;
    }
}

export async function requestPost(app, view, formData) {
    const url = `/${app}/${view}/`;
    console.log('POST request URL:', url);
    try {
        return await Api.post(url, formData);
    } catch (error) {
        console.error(`Erreur lors du chargement de ${app}-${view} :`, error);
        throw error;
    }
}

export async function requestDelete(app, view, ressourceId) {
    const url = `/${app}/${view}/${ressourceId}/`;

    try {
        return await Api.delete(url);
    } catch (error) {
        console.error(`Erreur lors de la suppression de ${app}-${view} avec ID ${ressourceId} :`, error);
        throw error;
    }
}
