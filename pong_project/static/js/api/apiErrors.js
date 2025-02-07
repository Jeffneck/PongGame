"use strict";
export class RequestError extends Error {
  constructor(message, status = null) {
    super(message);
    this.name = "RequestError";
    this.status = status;
  }
}

export class HTTPError extends RequestError {
  constructor(message, status) {
    super(message, status);
    this.name = "HTTPError";
  }
}

export class ContentTypeError extends RequestError {
  constructor(message) {
    super(message);
    this.name = "ContentTypeError";
  }
}

export class NetworkError extends RequestError {
  constructor(message) {
    super(message);
    this.name = "NetworkError";
  }
}
