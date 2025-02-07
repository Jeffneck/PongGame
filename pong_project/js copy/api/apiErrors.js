//api/apiErrors.js

// Classe de base pour les erreurs spécifiques à la requête
export class RequestError extends Error {
    constructor(message, status = null) {
        super(message);
        this.name = "RequestError";
        this.status = status; // Le code HTTP, si disponible
    }
}

// Erreur pour les réponses HTTP non réussies
export class HTTPError extends RequestError {
    constructor(message, status) {
        super(message, status);
        this.name = "HTTPError";
    }
}

// Erreur pour un problème de format inattendu dans la réponse
export class ContentTypeError extends RequestError {
    constructor(message) {
        super(message);
        this.name = "ContentTypeError";
    }
}

// Erreur pour un problème réseau (fetch lui-même échoue)
export class NetworkError extends RequestError {
    constructor(message) {
        super(message);
        this.name = "NetworkError";
    }
}