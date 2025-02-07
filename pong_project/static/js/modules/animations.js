"use strict";
export function adjustBurgerHeight() {
  const navAndMarginHeight = 66;
  const availableHeight = window.innerHeight - navAndMarginHeight;
  document.documentElement.style.setProperty('--burger-height', `${availableHeight}px`);
}

export function adjustSinNavHeight() {
  const navAndMarginHeight = 50;
  const availableHeight = window.innerHeight - navAndMarginHeight;
  document.documentElement.style.setProperty('--sin-nav-height', `${availableHeight}px`);
}

function adjustContainer(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;
  const threshold = 50;
  if (container.scrollHeight > window.innerHeight - threshold) {
    container.classList.remove('center-content');
    container.classList.add('normal-content');
  } else {
    container.classList.add('center-content');
    container.classList.remove('normal-content');
  }
}

export function adjustContainerIfExists(containerId) {
  const container = document.getElementById(containerId);
  if (container) {
    adjustContainer(containerId);
  }
}

export function adjustAllContainers() {
  window.addEventListener('resize', () => {
    adjustBurgerHeight();
    adjustSinNavHeight();
    adjustContainerIfExists('login');
    adjustContainerIfExists('register');
    adjustContainerIfExists('bracket_tournament');
  });
}
