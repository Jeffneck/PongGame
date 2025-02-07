"use strict";
export function isTouchDevice() {
  return Boolean(
    ('ontouchstart' in window) || 
    (navigator.maxTouchPoints && navigator.maxTouchPoints > 0) || 
    (navigator.msMaxTouchPoints && navigator.msMaxTouchPoints > 0)
  );
}

export function resetScrollPosition() {
  const scrollingElement = document.scrollingElement || document.documentElement;
  scrollingElement.scrollTop = 0;
}
