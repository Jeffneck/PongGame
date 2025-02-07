// api/index.js
// contient uniquement les fonctions que l' on souhaite appeler depuis d'autres fichiers

export { requestGet, requestPost , requestDelete} from './api.js';
export { RequestError, HTTPError, ContentTypeError, NetworkError } from './apiErrors.js';
