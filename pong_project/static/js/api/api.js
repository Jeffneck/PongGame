import { navigateTo } from '../router.js';
import { HTTPError, ContentTypeError, NetworkError } from './apiErrors.js';
import { showStatusMessage } from '../tools/displayInfo.js';

const Api = {
  /**
   * Effectue une requête HTTP avec fetch en utilisant FormData.
   * @param {string} url - L'URL complète de la ressource.
   * @param {string} method - La méthode HTTP (GET, POST, PUT, DELETE).
   * @param {FormData|null} formData - Les données à envoyer dans le corps de la requête.
   * @param {Object} customHeaders - Headers supplémentaires à ajouter.
   * @returns {Promise} - Une promesse résolue avec les données JSON ou rejetée en cas d'erreur.
   */
  async request(url, method = 'GET', formData = null, customHeaders = {}) {
    try {
      // Prépare et fusionne les en-têtes (CSRF et JWT)
      const headers = { ...this.prepareHeaders(), ...customHeaders };

      // Vérification et renouvellement du token si nécessaire
      const jwtAccessToken = this.getJWTaccessToken();
      if (jwtAccessToken && this.isTokenExpiringSoon(jwtAccessToken)) {
        console.warn('Access token sur le point d\'expirer, tentative de renouvellement...');
        const newToken = await this.handleTokenRefresh();
        if (newToken) {
          headers['Authorization'] = `Bearer ${newToken}`;
        }
      }

      // Envoi de la requête
      let response = await this.sendRequest(url, method, formData, headers);

       // Si la réponse est un 401, on lit le JSON pour distinguer le type d'erreur
       // Gestion des erreurs d'authentification
       if (response.status === 401) {
        const data = await response.json(); // lecture unique
        if (data.error_code === 'not_authenticated') {
          showStatusMessage(data.message, 'error');
          navigateTo(data.redirect);
          return; // On arrête ici
        } else {
          response = await this.handleUnauthorized(url, method, formData, customHeaders);
        }
      } else if (response.status === 403) {
        const data = await response.json(); // lecture unique
        if (data.error_code === 'auth_partial_required') {
          showStatusMessage(data.message, 'error');
          navigateTo(data.redirect);
          return; // On arrête ici
        } else {
          throw new HTTPError(data.message || 'Erreur inconnue.', response.status, data.error_code);
        }
      }
      return await this.handleResponse(response);
    } catch (error) {
      if (error instanceof TypeError) {
        throw new NetworkError('Échec réseau : ' + error.message);
      }
      throw error;
    }
  },

  /**
   * Prépare les en-têtes de la requête avec CSRF et JWT.
   * @returns {Object} - Les en-têtes préparés.
   */
  prepareHeaders() {
    const headers = {
      'X-CSRFToken': this.getCSRFToken(),
    };

    const jwtAccessToken = this.getJWTaccessToken();
    if (jwtAccessToken) {
      headers['Authorization'] = `Bearer ${jwtAccessToken}`;
    }

    return headers;
  },

  /**
   * Vérifie si le token expire dans moins de 5 minutes.
   * @param {string} token - Le token JWT.
   * @returns {boolean} - True si le token expire bientôt.
   */
  isTokenExpiringSoon(token) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Math.floor(Date.now() / 1000);
      return payload.exp - currentTime < 300; // Moins de 5 minutes
    } catch (error) {
      console.error('Erreur lors de la vérification de l\'expiration du token :', error);
      return true;
    }
  },

  /**
   * Envoie une requête fetch avec les paramètres fournis.
   */
  async sendRequest(url, method, formData, headers) {
    return fetch(url, {
      method,
      headers,
      body: method !== 'GET' && formData instanceof FormData ? formData : undefined,
    });
  },

  /**
   * Gère le cas d'une réponse 401 en essayant de rafraîchir le token.
   */
  async handleUnauthorized(url, method, formData, customHeaders) {
    console.warn('Accès non autorisé, tentative de rafraîchissement du token...');
    const newAccessToken = await this.handleTokenRefresh();

    if (newAccessToken) {
      // Mise à jour des en-têtes avec le nouveau token
      const updatedHeaders = {
        ...this.prepareHeaders(),
        ...customHeaders,
        'Authorization': `Bearer ${newAccessToken}`,
      };

      const response = await this.sendRequest(url, method, formData, updatedHeaders);
      if (!response.ok) {
        throw new HTTPError(
          response.statusText || 'Échec après rafraîchissement du token',
          response.status
        );
      }
      return response;
    } else {
      throw new HTTPError('Impossible de rafraîchir le token.', 401);
    }
  },

  /**
   * Rafraîchit le token d'accès en utilisant le refresh token.
   */
  async handleTokenRefresh() {
    const jwtRefreshToken = this.getJWTrefreshToken();
    if (!jwtRefreshToken) {
      console.error('Aucun refresh token disponible.');
      return null;
    }

    try {
      const response = await fetch('/accounts/refreshJwt/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCSRFToken(),
        },
        body: JSON.stringify({ refresh_token: jwtRefreshToken }),
      });

      if (response.ok) {
        const data = await response.json();
        const newAccessToken = data.access_token;
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

  /**
   * Gère la réponse fetch en fonction du type de contenu.
   */
  async handleResponse(response) {
    const contentType = response.headers.get('Content-Type');

    if (response.ok && contentType && contentType.includes('application/json')) {
      return response.json();
    } else if (!response.ok && contentType && contentType.includes('application/json'))
    {
        if (response.status === 302) {
            console.warn('Redirection détectée :', response.url);
            navigateTo(response.url);
            return; // On ne retourne pas de donnée
          }
        const errorData = await response.json();
        throw new HTTPError(errorData.message || 'Erreur inconnue.', response.status);
    } else {
      throw new HTTPError('Réponse inattendue.', response.status);
    }
  },

  // --- Fonctions utilitaires pour la gestion des tokens ---

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

  // --- Méthodes pour les requêtes HTTP spécifiques ---

  async get(url) {
    return this.request(url, 'GET');
  },

  async post(url, formData) {
    return this.request(url, 'POST', formData);
  },

  async put(url, formData) {
    return this.request(url, 'PUT', formData);
  },

  async delete(url) {
    return this.request(url, 'DELETE');
  }
};

// --- Fonctions exportées pour simplifier les appels dans d'autres fichiers ---

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
