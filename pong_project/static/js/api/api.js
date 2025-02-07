"use strict";
import { navigateTo } from '../router.js';
import { HTTPError, ContentTypeError, NetworkError } from './apiErrors.js';
import { showStatusMessage } from '../tools/displayInfo.js';
import { clearSessionAndUI } from '../tools/clearSession.js';

// Fonction utilitaire pour forcer la déconnexion de l'utilisateur
function forceLogout(message) {
  showStatusMessage(message, "error");
  setTimeout(() => { clearSessionAndUI(); }, 1000);
}

const Api = {
  /**
   * Fonction principale pour effectuer une requête HTTP.
   * Vérifie et rafraîchit le token d'accès si nécessaire.
   */
  async request(url, method = "GET", formData = null, customHeaders = {}) {
    try {
      // Prépare les headers (CSRF et Authorization)
      const headers = { ...this.prepareHeaders(), ...customHeaders };

      // Vérifie si l’access token expire bientôt et tente de le rafraîchir
      const jwtAccessToken = this.getJWTaccessToken();
      if (jwtAccessToken && this.isTokenExpiringSoon(jwtAccessToken)) {
        console.warn("Access token sur le point d'expirer, tentative de rafraîchissement...");
        const newToken = await this.handleTokenRefresh();
        if (newToken) {
          headers["Authorization"] = `Bearer ${newToken}`;
        } else {
          // Si le token ne peut pas être rafraîchi, on force la déconnexion
          forceLogout("Votre session a expiré, veuillez vous reconnecter.");
          return; // Arrête l'exécution de la requête
        }
      }

      // Effectue la requête
      let response = await this.sendRequest(url, method, formData, headers);

      // Gère les réponses 401 et 403
      if (response.status === 401) {
        const data = await response.json();
        // Si le code d'erreur indique que l'utilisateur n'est pas authentifié, on se contente d'afficher le message d'erreur
        if (data.error_code === "not_authenticated") {
          showStatusMessage(data.message, "error");
          return;
        }else if (data.error_code === "forbidden") {
          showStatusMessage(data.message, "error");
          navigateTo(data.redirect);
          return;
        }
        else if  (data.error_code === "token-error"){
          response = await this.handleUnauthorized(url, method, formData, customHeaders);
          
        }else {
          showStatusMessage(data.message, "error");
          return;
        }
      } else if (response.status === 403) {
        const data = await response.json();
        if (data.error_code === "auth_partial_required") {
          showStatusMessage(data.message, "error");
          forceLogout(data.message || "Session incomplète, reconnectez-vous.");
          return;
        } else {
          throw new HTTPError(data.message || "Erreur inconnue.", response.status);
        }
      }
      return await this.handleResponse(response);
    } catch (error) {
      if (error instanceof TypeError) {
        throw new NetworkError("Échec réseau : " + error.message);
      }
      // En cas d'erreur 401, forcer la déconnexion
      if (error instanceof HTTPError && error.status === 401) {
        forceLogout(error.message || "Session expirée, reconnectez-vous.");
      }
      throw error;
    }
  },

  /**
   * Prépare les headers en incluant le token CSRF et, s’il existe, le token JWT.
   */
  prepareHeaders() {
    const headers = {
      "X-CSRFToken": this.getCSRFToken(),
    };
    const jwtAccessToken = this.getJWTaccessToken();
    if (jwtAccessToken) {
      headers["Authorization"] = `Bearer ${jwtAccessToken}`;
    }
    return headers;
  },

  /**
   * Vérifie si le token expire dans moins de 5 minutes.
   */
  isTokenExpiringSoon(token) {
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      const currentTime = Math.floor(Date.now() / 1000);
      return payload.exp - currentTime < 300;
    } catch (error) {
      console.error("Erreur lors de la vérification de l'expiration du token :", error);
      return true;
    }
  },

  /**
   * Effectue la requête fetch avec la configuration fournie.
   */
  async sendRequest(url, method, formData, headers) {
    return fetch(url, {
      method,
      headers,
      body: method !== "GET" && formData instanceof FormData ? formData : undefined,
    });
  },

  /**
   * En cas d'erreur d'autorisation, tente de rafraîchir le token et réessaie la requête.
   */
  async handleUnauthorized(url, method, formData, customHeaders) {
    console.warn("Accès non autorisé, tentative de rafraîchissement du token...");
    const newAccessToken = await this.handleTokenRefresh();
    if (newAccessToken) {
      const updatedHeaders = {
        ...this.prepareHeaders(),
        ...customHeaders,
        Authorization: `Bearer ${newAccessToken}`,
      };
      const response = await this.sendRequest(url, method, formData, updatedHeaders);
      if (!response.ok) {
        throw new HTTPError(
          response.statusText || "Échec après rafraîchissement du token",
          response.status
        );
      }
      return response;
    } else {
      throw new HTTPError("Impossible de rafraîchir le token.", 401);
    }
  },

  /**
   * Rafraîchit le token d'accès en utilisant le refresh token.
   */
  async handleTokenRefresh() {
    const jwtRefreshToken = this.getJWTrefreshToken();
    if (!jwtRefreshToken) {
      console.error("Aucun refresh token disponible.");
      return null;
    }
    try {
      // Créez un FormData et ajoutez-y le refresh token
      const formData = new FormData();
      formData.append("refresh_token", jwtRefreshToken);
      
        // Préparez les headers avec le token CSRF et, s'il existe, le token JWT
      const headers = {
        "X-CSRFToken": this.getCSRFToken()
      };

        const jwtAccessToken = this.getJWTaccessToken();
        if (jwtAccessToken) {
          headers["Authorization"] = `Bearer ${jwtAccessToken}`;
        }

  
      // Effectuez la requête fetch directement sans passer par this.post()
      const response = await fetch("/accounts/refreshJwt/", {
        method: "POST",
        body: formData,
        headers,
      });
  
      if (!response.ok) {
        forceLogout("Impossible de rafraîchir le token, veuillez vous reconnecter.");
        console.error("Erreur HTTP lors du rafraîchissement du token:", response.status, response.statusText);
        return null;
      }
  
      // Analysez la réponse JSON
      const data = await response.json();
  
      if (data && data.access_token) {
        const newAccessToken = data.access_token;
        localStorage.setItem("access_token", newAccessToken);
        return newAccessToken;
      } else {
        console.error("Erreur lors du rafraîchissement du token:", data ? data.message : "Aucune réponse");
        return null;
      }
    } catch (error) {
      console.error("Échec du rafraîchissement du token :", error);
      return null;
    }
  },

  /**
   * Traite la réponse du serveur en fonction du Content-Type.
   */
  async handleResponse(response) {
    const contentType = response.headers.get("Content-Type");
    if (response.ok && contentType && contentType.includes("application/json")) {
      return response.json();
    } else if (!response.ok && contentType && contentType.includes("application/json")) {
      const errorData = await response.json();
      throw new HTTPError(errorData.message || "Erreur inconnue.", response.status);
    } else {
      throw new HTTPError("Réponse inattendue.", response.status);
    }
  },

  getCSRFToken() {
    const cookie = document.cookie.split(";").find(c => c.trim().startsWith("csrftoken="));
    return cookie ? cookie.trim().substring("csrftoken=".length) : "";
  },

  getJWTaccessToken() {
    return localStorage.getItem("access_token") || null;
  },

  getJWTrefreshToken() {
    return localStorage.getItem("refresh_token") || null;
  },

  async get(url) {
    return this.request(url, "GET");
  },

  async post(url, formData) {
    return this.request(url, "POST", formData);
  },

  async put(url, formData) {
    return this.request(url, "PUT", formData);
  },

  async delete(url) {
    return this.request(url, "DELETE");
  },
};

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
  console.debug("POST request URL:", url);
  try {
    return await Api.post(url, formData);
  } catch (error) {
    console.error(`Erreur lors du POST vers ${app}-${view} :`, error);
    throw error;
  }
}

export async function requestDelete(app, view, resourceId) {
  const url = `/${app}/${view}/${resourceId}/`;
  try {
    return await Api.delete(url);
  } catch (error) {
    console.error(`Erreur lors de la suppression de ${app}-${view} avec ID ${resourceId} :`, error);
    throw error;
  }
}

export { RequestError, HTTPError, ContentTypeError, NetworkError } from "./apiErrors.js";
