// game/controls.js


export function initializeGameControls(controlType) {
    const player = document.querySelector('.player');
    const gameContainer = document.querySelector('.game-container');
    const tutorialBox = document.querySelector('.tutorial-box');
    let containerWidth = gameContainer.offsetWidth;
    let containerHeight = gameContainer.offsetHeight - 50;
    const collectibleCount = 9;
    const collectibles = [];
    let direction = { x: 1, y: 0 }; // Par défaut, déplacement vers la droite
    const playerSpeed = 3;
    let playerX = 0;
    let playerY = containerHeight / 2 - 15; // Milieu vertical
    const keysPressed = {}; // Stocke les touches enfoncées
    let lastDiagonalDirection = null; // Stocke la dernière direction diagonale
    let touchStartX = null; // Stocke la position X du toucher initial
    let touchStartY = null; // Stocke la position Y du toucher initial

    // Calcul des dimensions de la box
    const tutorialRect = {
        left: 0,
        top: 0,
        right: tutorialBox.offsetWidth,
        bottom: tutorialBox.offsetHeight,
    };

    // Initialisation de la position du joueur
    player.style.left = `${playerX}px`;
    player.style.top = `${playerY}px`;

    // Fonction pour éviter que les collectibles ne sortent du conteneur pendant un redimensionnement
	function updateContainerDimensions() {
		containerWidth = gameContainer.offsetWidth;
		containerHeight = gameContainer.offsetHeight - 50;
	
		// Mettre à jour les dimensions dynamiques de la tutorial-box
		tutorialRect.left = tutorialBox.offsetLeft;
		tutorialRect.top = tutorialBox.offsetTop;
		tutorialRect.right = tutorialBox.offsetLeft + tutorialBox.offsetWidth;
		tutorialRect.bottom = tutorialBox.offsetTop + tutorialBox.offsetHeight;
	
		// Réajuster les collectibles pour rester dans les limites du conteneur
		collectibles.forEach((collectible) => {
			let collectibleX = parseFloat(collectible.style.left);
			let collectibleY = parseFloat(collectible.style.top);
	
			// Si le collectible est hors des nouvelles limites, repositionner
			if (collectibleX + 30 > containerWidth) {
				collectibleX = containerWidth - 30;
			}
			if (collectibleY + 30 > containerHeight) {
				collectibleY = containerHeight - 30;
			}
	
			// Si le collectible est dans la zone de la tutorial-box
			if (
				collectibleX + 30 > tutorialRect.left &&
				collectibleX < tutorialRect.right &&
				collectibleY + 30 > tutorialRect.top &&
				collectibleY < tutorialRect.bottom
			) {
				// Répositionner autour de la tutorial-box en fonction de l’espace disponible
				const spaceLeft = tutorialRect.left;
				const spaceRight = containerWidth - tutorialRect.right;
				const spaceTop = tutorialRect.top;
				const spaceBottom = containerHeight - tutorialRect.bottom;
	
				if (spaceRight >= 30) {
					// Place le collectible à droite
					collectibleX = tutorialRect.right + 1;
					collectibleY = Math.random() * (containerHeight - 30);
					collectibleY = Math.max(
						Math.min(collectibleY, containerHeight - 30),
						0
					);
				} else if (spaceLeft >= 30) {
					// Place le collectible à gauche
					collectibleX = tutorialRect.left - 30 - 1;
					collectibleY = Math.random() * (containerHeight - 30);
					collectibleY = Math.max(
						Math.min(collectibleY, containerHeight - 30),
						0
					);
				} else if (spaceBottom >= 30) {
					// Place le collectible en bas
					collectibleY = tutorialRect.bottom + 1;
					collectibleX = Math.random() * (containerWidth - 30);
					collectibleX = Math.max(
						Math.min(collectibleX, containerWidth - 30),
						0
					);
				} else if (spaceTop >= 30) {
					// Place le collectible en haut
					collectibleY = tutorialRect.top - 30 - 1;
					collectibleX = Math.random() * (containerWidth - 30);
					collectibleX = Math.max(
						Math.min(collectibleX, containerWidth - 30),
						0
					);
				} else {
					// Si aucune place n'est disponible, masquer le collectible
					collectible.style.display = 'none';
					return;
				}
			}
	
			// Vérifier que le collectible reste dans les limites visibles du conteneur
			collectibleX = Math.min(
				Math.max(collectibleX, 0),
				containerWidth - 30
			);
			collectibleY = Math.min(
				Math.max(collectibleY, 0),
				containerHeight - 30
			);
	
			// Appliquer les nouvelles positions
			collectible.style.left = `${collectibleX}px`;
			collectible.style.top = `${collectibleY}px`;
	
			// Si l'écran est tellement réduit que seule la tutorial-box est visible
			if (
				containerWidth <= tutorialRect.right &&
				containerHeight <= tutorialRect.bottom
			) {
				collectible.style.display = 'none'; // Cacher les collectibles
			} else {
				collectible.style.display = ''; // Réafficher normalement sinon
			}
		});
	
		// Maintenir le joueur dans les limites du conteneur
		if (playerX + player.offsetWidth > containerWidth) {
			playerX = containerWidth - player.offsetWidth;
		}
		if (playerY + player.offsetHeight > containerHeight) {
			playerY = containerHeight - player.offsetHeight;
		}
		if (playerX < 0) {
			playerX = 0;
		}
		if (playerY < 0) {
			playerY = 0;
		}
	
		player.style.left = `${playerX}px`;
		player.style.top = `${playerY}px`;
	}
	

    function createCollectibles() {
        collectibles.forEach((col) => col.remove()); // Supprime les collectibles existants
        collectibles.length = 0;

        for (let i = 0; i < collectibleCount; i++) {
            let collectible;
            let isValidPosition = false;

            while (!isValidPosition) {
                collectible = document.createElement('div');
                collectible.className = 'collectible';
                const randomX = Math.random() * (containerWidth - 30);
                const randomY = Math.random() * (containerHeight - 30);

                // Vérifie que le collectible n'est pas dans la zone de la tutorial-box
                if (
                    !(
                        randomX >= tutorialRect.left &&
                        randomX <= tutorialRect.right &&
                        randomY >= tutorialRect.top &&
                        randomY <= tutorialRect.bottom
                    )
                ) {
                    isValidPosition = true;
                    collectible.style.left = `${randomX}px`;
                    collectible.style.top = `${randomY}px`;
                    gameContainer.appendChild(collectible);
                    collectibles.push(collectible);
                }
            }
        }
    }

    function movePlayer() {
        const length = Math.sqrt(direction.x ** 2 + direction.y ** 2);
        const normalizedDirection = {
            x: (direction.x / length) * playerSpeed,
            y: (direction.y / length) * playerSpeed,
        };

        playerX += normalizedDirection.x;
        playerY += normalizedDirection.y;

        if (playerX < 0) {
            playerX = containerWidth - player.offsetWidth;
        } else if (playerX > containerWidth - player.offsetWidth) {
            playerX = 0;
        }

        if (playerY < 0) {
            playerY = containerHeight - player.offsetHeight;
        } else if (playerY > containerHeight - player.offsetHeight) {
            playerY = 0;
        }

        // Empêcher le joueur d'entrer dans la zone de la tutorial-box
        if (
            playerX + player.offsetWidth >= tutorialRect.left &&
            playerX <= tutorialRect.right &&
            playerY + player.offsetHeight >= tutorialRect.top &&
            playerY <= tutorialRect.bottom
        ) {
            // Vérifier la direction pour rebondir correctement
            if (direction.x > 0) {
                playerX = tutorialRect.right; // Sortir par la droite
            } else if (direction.x < 0) {
                playerX = tutorialRect.left - player.offsetWidth; // Sortir par la gauche
            }

            if (direction.y > 0) {
                playerY = tutorialRect.bottom; // Sortir par le bas
            } else if (direction.y < 0) {
                playerY = tutorialRect.top - player.offsetHeight; // Sortir par le haut
            }
        }

        player.style.left = `${playerX}px`;
        player.style.top = `${playerY}px`;

        collectibles.forEach((collectible, index) => {
            const collectibleRect = collectible.getBoundingClientRect();
            const playerRect = player.getBoundingClientRect();

            if (
                playerRect.left < collectibleRect.right &&
                playerRect.right > collectibleRect.left &&
                playerRect.top < collectibleRect.bottom &&
                playerRect.bottom > collectibleRect.top
            ) {
                collectible.remove();
                collectibles.splice(index, 1);

                if (collectibles.length === 0) {
                    setTimeout(createCollectibles, 500);
                }
            }
        });
    }

    // Gestion des contrôles clavier
    function updateDirection() {
        if (keysPressed['ArrowUp'] && keysPressed['ArrowLeft']) {
            direction = { x: -1, y: -1 };
            lastDiagonalDirection = { x: -1, y: -1 };
        } else if (keysPressed['ArrowUp'] && keysPressed['ArrowRight']) {
            direction = { x: 1, y: -1 };
            lastDiagonalDirection = { x: 1, y: -1 };
        } else if (keysPressed['ArrowDown'] && keysPressed['ArrowLeft']) {
            direction = { x: -1, y: 1 };
            lastDiagonalDirection = { x: -1, y: 1 };
        } else if (keysPressed['ArrowDown'] && keysPressed['ArrowRight']) {
            direction = { x: 1, y: 1 };
            lastDiagonalDirection = { x: 1, y: 1 };
        } else if (keysPressed['ArrowUp']) {
            direction = { x: 0, y: -1 };
        } else if (keysPressed['ArrowDown']) {
            direction = { x: 0, y: 1 };
        } else if (keysPressed['ArrowLeft']) {
            direction = { x: -1, y: 0 };
        } else if (keysPressed['ArrowRight']) {
            direction = { x: 1, y: 0 };
        } else if (lastDiagonalDirection) {
            direction = lastDiagonalDirection;
        }
        lastDiagonalDirection = direction;
    }

    function handleTouchStart(event) {
        const touch = event.touches[0];
        touchStartX = touch.clientX;
        touchStartY = touch.clientY;
    }

    function handleTouchMove(event) {
        if (!touchStartX || !touchStartY) return;

        const touchEndX = event.touches[0].clientX;
        const touchEndY = event.touches[0].clientY;

        const diffX = touchEndX - touchStartX;
        const diffY = touchEndY - touchStartY;

        const threshold = 5;

        if (Math.abs(diffX) > Math.abs(diffY)) {
            direction = { x: diffX > 0 ? 1 : -1, y: 0 };
        } else {
            direction = { x: 0, y: diffY > 0 ? 1 : -1 };
        }

        touchStartX = touchEndX;
        touchStartY = touchEndY;
    }

    if (controlType === 'keyboard') {
        document.addEventListener('keydown', (e) => {
            keysPressed[e.key] = true;
            updateDirection();
        });

        document.addEventListener('keyup', (e) => {
            keysPressed[e.key] = false;
        });
    }

    function gameLoop() {
        movePlayer();
        requestAnimationFrame(gameLoop);
    }

    if (controlType === 'touch') {
        gameContainer.addEventListener('touchstart', handleTouchStart, { passive: false });
        gameContainer.addEventListener('touchmove', handleTouchMove, { passive: false });
    }

    window.addEventListener('resize', () => {
        updateContainerDimensions();
    });

    updateContainerDimensions();
    createCollectibles();
    gameLoop();
}

// export function initializeGameControls(controlType) {
//     const player = document.querySelector('.player');
//     const gameContainer = document.querySelector('.game-container');
//     if (!player || !gameContainer) return;

//     let containerWidth = gameContainer.offsetWidth;
//     let containerHeight = gameContainer.offsetHeight;
//     const collectibleCount = 9;
//     const collectibles = [];
//     let direction = { x: 1, y: 0 };
//     const playerSpeed = 3;
//     let playerX = 0;
//     let playerY = containerHeight / 2 - 15;
//     const keysPressed = {};
//     let lastDiagonalDirection = null;
//     let touchStartX = null;
//     let touchStartY = null;

//     function updateContainerDimensions() {
//         containerWidth = gameContainer.offsetWidth;
//         containerHeight = gameContainer.offsetHeight - 50;
//         collectibles.forEach(collectible => {
//             let cX = parseFloat(collectible.style.left);
//             let cY = parseFloat(collectible.style.top);
//             if (cX + 30 > containerWidth) {
//                 collectible.style.left = `${containerWidth - 30}px`;
//             }
//             if (cY + 30 > containerHeight) {
//                 collectible.style.top = `${containerHeight - 30}px`;
//             }
//         });
//     }

//     function createCollectibles() {
//         collectibles.forEach(col => col.remove());
//         collectibles.length = 0;
//         for (let i = 0; i < collectibleCount; i++) {
//             const collectible = document.createElement('div');
//             collectible.className = 'collectible';
//             collectible.style.left = `${Math.random() * (containerWidth - 30)}px`;
//             collectible.style.top = `${Math.random() * (containerHeight - 30)}px`;
//             gameContainer.appendChild(collectible);
//             collectibles.push(collectible);
//         }
//     }

//     function movePlayer() {
//         const length = Math.sqrt(direction.x ** 2 + direction.y ** 2);
//         const normalized = { x: (direction.x / length) * playerSpeed, y: (direction.y / length) * playerSpeed };
//         playerX += normalized.x;
//         playerY += normalized.y;

//         if (playerX < 0) playerX = containerWidth - player.offsetWidth;
//         else if (playerX > containerWidth - player.offsetWidth) playerX = 0;

//         if (playerY < 0) playerY = containerHeight - player.offsetHeight;
//         else if (playerY > containerHeight - player.offsetHeight) playerY = 0;

//         player.style.left = `${playerX}px`;
//         player.style.top = `${playerY}px`;

//         collectibles.forEach((c, i) => {
//             const cRect = c.getBoundingClientRect();
//             const pRect = player.getBoundingClientRect();
//             if (pRect.left < cRect.right && pRect.right > cRect.left && pRect.top < cRect.bottom && pRect.bottom > cRect.top) {
//                 c.remove();
//                 collectibles.splice(i, 1);
//                 if (collectibles.length === 0) {
//                     setTimeout(createCollectibles, 500);
//                 }
//             }
//         });
//     }

//     function updateDirection() {
//         if (keysPressed['ArrowUp'] && keysPressed['ArrowLeft']) {
//             direction = { x: -1, y: -1 };
//             lastDiagonalDirection = direction;
//         } else if (keysPressed['ArrowUp'] && keysPressed['ArrowRight']) {
//             direction = { x: 1, y: -1 };
//             lastDiagonalDirection = direction;
//         } else if (keysPressed['ArrowDown'] && keysPressed['ArrowLeft']) {
//             direction = { x: -1, y: 1 };
//             lastDiagonalDirection = direction;
//         } else if (keysPressed['ArrowDown'] && keysPressed['ArrowRight']) {
//             direction = { x: 1, y: 1 };
//             lastDiagonalDirection = direction;
//         } else if (keysPressed['ArrowUp']) {
//             direction = { x: 0, y: -1 };
//         } else if (keysPressed['ArrowDown']) {
//             direction = { x: 0, y: 1 };
//         } else if (keysPressed['ArrowLeft']) {
//             direction = { x: -1, y: 0 };
//         } else if (keysPressed['ArrowRight']) {
//             direction = { x: 1, y: 0 };
//         } else if (lastDiagonalDirection) {
//             direction = lastDiagonalDirection;
//         }
//     }

//     if (controlType === 'keyboard') {
//         document.addEventListener('keydown', (e) => {
//             keysPressed[e.key] = true;
//             updateDirection();
//         });
//         document.addEventListener('keyup', (e) => {
//             keysPressed[e.key] = false;
//             if (!keysPressed['ArrowUp'] && !keysPressed['ArrowDown'] && !keysPressed['ArrowLeft'] && !keysPressed['ArrowRight']) {
//                 if (lastDiagonalDirection) direction = lastDiagonalDirection;
//             }
//         });
//     }

//     if (controlType === 'touch') {
//         gameContainer.addEventListener('touchstart', e => {
//             const touch = e.touches[0];
//             touchStartX = touch.clientX;
//             touchStartY = touch.clientY;
//         }, { passive: false });

//         gameContainer.addEventListener('touchmove', e => {
//             if (!touchStartX || !touchStartY) return;
//             const touchEndX = e.touches[0].clientX;
//             const touchEndY = e.touches[0].clientY;
//             const diffX = touchEndX - touchStartX;
//             const diffY = touchEndY - touchStartY;
//             const threshold = 5;
//             if (Math.abs(diffX) > Math.abs(diffY)) {
//                 if (Math.abs(diffY) > threshold) {
//                     direction = { x: diffX > 0 ? 1 : -1, y: diffY > 0 ? 1 : -1 };
//                 } else {
//                     direction = { x: diffX > 0 ? 1 : -1, y: 0 };
//                 }
//             } else {
//                 if (Math.abs(diffX) > threshold) {
//                     direction = { x: diffX > 0 ? 1 : -1, y: diffY > 0 ? 1 : -1 };
//                 } else {
//                     direction = { x: 0, y: diffY > 0 ? 1 : -1 };
//                 }
//             }
//             touchStartX = touchEndX;
//             touchStartY = touchEndY;
//         }, { passive: false });
//     }

//     function gameLoop() {
//         movePlayer();
//         requestAnimationFrame(gameLoop);
//     }

//     window.addEventListener('resize', () => updateContainerDimensions());
//     updateContainerDimensions();
//     createCollectibles();
//     gameLoop();
// }
