"use strict";
export function displaySuccessMessage(elementId, message) {
  const element = document.getElementById(elementId);
  if (element) {
    element.textContent = message;
    element.style.color = 'green';
    element.style.display = 'block';
  } else {
    console.warn(`Élément ${elementId} introuvable.`);
  }
}

export function displayErrorMessage(elementId, message) {
  const element = document.getElementById(elementId);
  if (element) {
    element.textContent = message;
    element.style.color = 'red';
    element.style.display = 'block';
  } else {
    console.warn(`Élément ${elementId} introuvable.`);
  }
}

export function displayInfoMessage(elementId, message) {
  const element = document.getElementById(elementId);
  if (element) {
    element.textContent = message;
    element.style.color = 'blue';
    element.style.display = 'block';
  } else {
    console.warn(`Élément ${elementId} introuvable.`);
  }
}

export function clearMessage(elementId) {
  const element = document.getElementById(elementId);
  if (element) {
    element.textContent = '';
    element.style.display = 'none';
  } else {
    console.warn(`Élément ${elementId} introuvable.`);
  }
}

export function showStatusMessage(message, status) {
  const popup = document.getElementById('popup');
  const info = document.getElementById('info');
  if (info) {
    info.textContent = message;
  }
  popup.classList.remove('success', 'error', 'd-none', 'hide');
  if (status === 'success') {
    popup.classList.add('success');
  } else if (status === 'error') {
    popup.classList.add('error');
  }
  popup.classList.add('show');
  setTimeout(() => {
    popup.classList.remove('show');
    popup.classList.add('hide');
    setTimeout(() => popup.classList.add('d-none'), 500);
  }, 3000);
}
