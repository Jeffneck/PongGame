"use strict";
import { requestGet } from "../api/index.js";
import { updateHtmlContent } from "./domHandler.js";

export async function initializeNotFoundView() {
  try {
    const response = await requestGet('core', '404');
    if (response.status === 'success') {
      updateHtmlContent('#content', response.html);
    }
  } catch (error) {
    console.error("Erreur dans initializeNotFoundView :", error);
  }
}
