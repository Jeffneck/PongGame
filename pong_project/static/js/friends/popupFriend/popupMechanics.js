"use strict";
export function showFriendPopup(event, friendName) {
  event.stopPropagation();
  const popup = document.getElementById('friendPopup');
  if (!popup) return;
  document.getElementById('popupFriendName').innerText = friendName;
  popup.classList.remove('d-none');
  const popupWidth = popup.offsetWidth;
  const popupHeight = popup.offsetHeight;
  const menu = document.getElementById('burger-menu');
  const menuRect = menu.getBoundingClientRect();
  const mouseX = event.clientX - menuRect.left + menu.scrollLeft;
  const mouseY = event.clientY - menuRect.top + menu.scrollTop;
  let top, left;
  if (mouseX >= 240 && event.clientY <= 250) {
    top = mouseY + popupHeight;
    left = mouseX - popupWidth / 2;
  } else if (mouseX <= 240 && event.clientY <= 250) {
    top = mouseY + popupHeight;
    left = mouseX + popupWidth / 2;
  } else if (mouseX <= 240 && event.clientY >= 250) {
    top = mouseY;
    left = mouseX + popupWidth / 2;
  } else {
    top = mouseY;
    left = mouseX - popupWidth / 2;
  }
  popup.style.top = `${top}px`;
  popup.style.left = `${left}px`;
}

export function closePopupOnClickOutside(event) {
  const popup = document.getElementById('friendPopup');
  if (popup && !popup.contains(event.target) && !event.target.closest('.friend-item')) {
    popup.classList.add('d-none');
  }
}
