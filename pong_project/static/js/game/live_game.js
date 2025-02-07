/* live_game.js
 *
 * Centralise les fonctions communes pour :
 * dessiner le canvas, les bumpers et les powerups
 * lancer le jeu en co-routine avec le bouton startGame 
 * recevoir les notifications (envoyées par broadcast.py > consumers.py > websocket)
 *    detecter la position de tous les elements de jeu (gameState)
 *    afficher des animations aux lieux d'impacts de la balle /lieux d'apparition des bumpers et powerups 
 * 
 */

import { requestPost } from '../api/index.js';
import { createPowerupSVG, createBumperSVG } from './live_game_svg.js';
import { isTouchDevice } from "../tools/index.js";


export async function launchLiveGameWithOptions(gameId, userRole, urlStartButton) {
  const protocol = (window.location.protocol === 'https:') ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws/pong/${gameId}/`;

  let startGameSelector = null;
  let onStartGame = null;
  
  console.log(`userRole = ${userRole}`);
  if (urlStartButton) {
    // Sélectionner l'élément DOM correspondant au bouton de démarrage
    startGameSelector = document.querySelector("#startGameBtn");
    // Vérifier que l'élément a bien été trouvé
    if (!startGameSelector) {
      console.error("L'élément avec le sélecteur '#startGameBtn' n'a pas été trouvé.");
    }
    
    onStartGame = async (gameId) => {
      // Assurez-vous que startGameSelector est bien un élément DOM avant d'accéder à classList
      if (startGameSelector) {
        startGameSelector.classList.add('d-none');
      }
      const url = urlStartButton;
      const formData = new FormData();
      formData.append('game_id', gameId);
      formData.append('userRole', userRole);
  
      const response = await requestPost('game', url, formData);
      if (response.status !== 'success') {
        alert("Erreur lors du démarrage : " + response.message);
      }
    };
  }

  // fonction qui gere toute la logique de jeu à partir de notre config
  return initLiveGame({
    gameId,
    userRole,
    wsUrl,
    startGameSelector,
    onStartGame
  });
}


  // ========== initPowerupImages ==========
  
  function initPowerupImages(powerupImages) {
    // Initialise la map de type => Image()
    Object.keys(powerupImages).forEach(type => {
      powerupImages[type].src = createPowerupSVG(type);
    });
  }
  
  // ========== applyFlashEffect ==========
  
  function applyFlashEffect(gameState, duration = 300) {
    gameState.flash_effect = true;
    setTimeout(() => {
      gameState.flash_effect = false;
    }, duration);
  }



// ========== La grosse fonction initLiveGame ==========

/**
 * Initialise un "live game" (local ou online) dans le canvas.
 * @param {Object} config 
 *    config.gameId  : string
 *    config.userRole: "left" | "right" | "both"   // ex: "both" = local, "left" ou "right" = online
 *    config.wsUrl   : URL du WebSocket
 *    config.startGameSelector?: ID du bouton (ex: "#startGameBtn")
 *    config.onStartGame?: Function de callback pour lancer la partie 
 *                         (ex: faire un POST sur /start_online_game/ ou /start_local_game/)
   */
function initLiveGame(config) {
  return new Promise((resolve) => {
    // 1) Préparer les éléments HTML
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const startGameBtn = config.startGameSelector;
    console.log("Appareil tactile ?", isTouchDevice());
    cleanupGamePage();
    setupGamePage();
    // 2) Gérer le bouton "Start" (optionnel)
    if (startGameBtn && config.onStartGame) {
      // Débloquer le bouton après 3s (optionnel)
  //     setTimeout(() => { 
	// 	startGameBtn.style.opacity = "0.7";
  //       startGameBtn.disabled = false;
	    startGameBtn.classList.add("active");
	
	// }, 3000);
  
      // Clic => on appelle la callback onStartGame
      startGameBtn.addEventListener('click', async () => {
        await config.onStartGame()
        // await startGameWithCountdown(startGameBtn, config.onStartGame, config.gameId);
      });
    }



	// Draw visual effects / added
	function drawCollisionEffects() {
		collisionEffects.forEach(effect => {
			const age = effect.type.includes('spawn') ?
			  Date.now() - effect.startTime :
			  Date.now() - effect.startTime;
			const duration = effect.type.includes('spawn') ?
			  SPAWN_EFFECT_DURATION :
			  EXPIRE_EFFECT_DURATION;
			const progress = age / duration;
  
			ctx.save();
			ctx.globalAlpha = 1 - progress;
  
			switch(effect.type) {
				case 'paddle_collision':
					// Ripple effect
					const rippleSize = 20 + (progress * 40);
					ctx.strokeStyle = 'white';
					ctx.lineWidth = 3 * (1 - progress);
					ctx.beginPath();
					ctx.arc(effect.x, effect.y, rippleSize, 0, Math.PI * 2);
					ctx.stroke();
					break;
  
				// case 'border_collision':
				//     // Simple glow effect at collision point
				//     const glowSize = 20 * (1 - progress);
				//     ctx.shadowColor = 'white';
				//     ctx.shadowBlur = 15 * (1 - progress);
					
				//     ctx.beginPath();
				//     ctx.arc(effect.x, effect.border_side === 'up' ? 50 : 350, glowSize, 0, Math.PI * 2);
				//     ctx.fillStyle = 'rgba(255, 255, 255, ' + (1 - progress) + ')';
				//     ctx.fill();
				//     break;
  
				case 'bumper_collision':
					// Explosion effect
					const numParticles = 8;
					const radius = 30 * progress;
					ctx.strokeStyle = '#4169E1';
					ctx.lineWidth = 3 * (1 - progress);
					
					for (let i = 0; i < numParticles; i++) {
						const angle = (i / numParticles) * Math.PI * 2;
						const startX = effect.x + Math.cos(angle) * 10;
						const startY = effect.y + Math.sin(angle) * 10;
						const endX = effect.x + Math.cos(angle) * radius;
						const endY = effect.y + Math.sin(angle) * radius;
						
						ctx.beginPath();
						ctx.moveTo(startX, startY);
						ctx.lineTo(endX, endY);
						ctx.stroke();
					}
					break;
				case 'powerup_spawn':
					// Expanding circles with powerup color
					const circles = 3;
					ctx.strokeStyle = effect.color;
					ctx.lineWidth = 2;
					
					for (let i = 0; i < circles; i++) {
						const circleProgress = (progress + (i / circles)) % 1;
						const radius = circleProgress * 40;
						ctx.beginPath();
						ctx.arc(effect.x, effect.y, radius, 0, Math.PI * 2);
						ctx.stroke();
					}
  
					// Add sparkles
					const sparkles = 8;
					for (let i = 0; i < sparkles; i++) {
						const angle = (i / sparkles) * Math.PI * 2;
						const sparkleDistance = 20 + (progress * 20);
						const x = effect.x + Math.cos(angle) * sparkleDistance;
						const y = effect.y + Math.sin(angle) * sparkleDistance;
						
						ctx.beginPath();
						ctx.arc(x, y, 2, 0, Math.PI * 2);
						ctx.fillStyle = effect.color;
						ctx.fill();
					}
					break;
  
				case 'powerup_expire':
					// Imploding effect
					const fadeRadius = 20 * (1 - progress);
					ctx.strokeStyle = effect.color;
					ctx.lineWidth = 2 * (1 - progress);
					
					// Shrinking circle
					ctx.beginPath();
					ctx.arc(effect.x, effect.y, fadeRadius, 0, Math.PI * 2);
					ctx.stroke();
					
					// Particles moving inward
					const particles = 6;
					for (let i = 0; i < particles; i++) {
						const angle = (i / particles) * Math.PI * 2;
						const distance = fadeRadius * 2;
						const x = effect.x + Math.cos(angle) * distance * progress;
						const y = effect.y + Math.sin(angle) * distance * progress;
						
						ctx.beginPath();
						ctx.arc(x, y, 2, 0, Math.PI * 2);
						ctx.fill();
					}
					break;
  
				case 'bumper_spawn':
					// Expanding diamond pattern
					ctx.strokeStyle = '#4169E1';
					ctx.lineWidth = 2;
					const size = 40 * progress;
					const rotation = progress * Math.PI;
					
					ctx.translate(effect.x, effect.y);
					ctx.rotate(rotation);
					
					// Inner diamond
					ctx.beginPath();
					ctx.moveTo(0, -size);
					ctx.lineTo(size, 0);
					ctx.lineTo(0, size);
					ctx.lineTo(-size, 0);
					ctx.closePath();
					ctx.stroke();
					
					// Outer diamond
					ctx.beginPath();
					ctx.moveTo(0, -size * 1.5);
					ctx.lineTo(size * 1.5, 0);
					ctx.lineTo(0, size * 1.5);
					ctx.lineTo(-size * 1.5, 0);
					ctx.closePath();
					ctx.stroke();
					break;
  
				case 'bumper_expire':
					// Dissolving rings effect
					ctx.strokeStyle = '#4169E1';
					ctx.lineWidth = 2 * (1 - progress);
					
					const rings = 3;
					for (let i = 0; i < rings; i++) {
						const ringProgress = (progress + (i / rings)) % 1;
						const ringRadius = 20 * ringProgress;
						
						ctx.beginPath();
						ctx.arc(effect.x, effect.y, ringRadius, 0, Math.PI * 2);
						ctx.stroke();
						
						// Add dissolving particles
						const particleCount = 8;
						for (let j = 0; j < particleCount; j++) {
							const particleAngle = (j / particleCount) * Math.PI * 2;
							const distance = ringRadius * (1 + progress);
							const px = effect.x + Math.cos(particleAngle) * distance;
							const py = effect.y + Math.sin(particleAngle) * distance;
							
							ctx.fillStyle = '#4169E1';
							ctx.fillRect(px - 1, py - 1, 2, 2);
						}
					}
					break;
			}
			ctx.restore();
		});
	}


	function drawCountdown() {
    if (typeof gameState.countdown !== 'undefined') {
      ctx.save();
      ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
  
      ctx.fillStyle = 'white';
      ctx.font = 'bold 80px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.shadowColor = 'rgba(255, 255, 255, 0.8)';
      ctx.shadowBlur = 20;
      ctx.fillText(gameState.countdown, canvas.width / 2, canvas.height / 3);
      ctx.restore();
    }
	}
  
    // 3) Mise en place du redimensionnement du canvas
    const ORIGINAL_WIDTH = 800;
    const ORIGINAL_HEIGHT = 400;
    let scale = 1;

	    // Const for visual effects on notifications / added
		const collisionEffects = [];
		const EFFECT_DURATION = 300;
		const SPAWN_EFFECT_DURATION = 500;
		const EXPIRE_EFFECT_DURATION = 300;
	  
		// spawn visual effect / added
		function createSpawnEffect(type, x, y, effectType, color) {
		  const effect = {
			  type,
			  x,
			  y,
			  effectType,
			  color: color || '#FFFFFF',
			  startTime: Date.now(),
			  alpha: 1
		  };
		  collisionEffects.push(effect);
		  
		  setTimeout(() => {
			  const index = collisionEffects.indexOf(effect);
			  if (index > -1) {
				  collisionEffects.splice(index, 1);
			  }
		  }, type.includes('spawn') ? SPAWN_EFFECT_DURATION : EXPIRE_EFFECT_DURATION);
	  }
	
	  // collision visual effects / added
	  function createCollisionEffect(type, x, y, color) {
		const effect = {
			type,
			x,
			y,
			color,
			startTime: Date.now(),
			alpha: 1
		};
		collisionEffects.push(effect);
		
		// Remove effect after duration
		setTimeout(() => {
			const index = collisionEffects.indexOf(effect);
			if (index > -1) {
				collisionEffects.splice(index, 1);
			}
		}, EFFECT_DURATION);
	  }

    
      // --- Pour gérer l'orientation sur mobile tactile ---
    function onOrientationChange() {
      // Petit délai si besoin pour que la taille soit bien mise à jour
      setTimeout(handleresizeTactile, 200);
    }

    // --- Setup de la page de jeu ---
   async function setupGamePage() {
      if (isTouchDevice()) {
        console.log("Mode tactile activé");
        window.addEventListener('resize', handleresizeTactile);
        window.addEventListener('orientationchange', onOrientationChange);
        handleresizeTactile();
      } else {
        console.log("Mode non tactile activé");
        window.addEventListener('resize', handleResize);
        handleResize();
      }
    }

    // --- Cleanup de la page de jeu ---
    function cleanupGamePage() {
      if (isTouchDevice()) {
        window.removeEventListener('resize', handleresizeTactile);
        window.removeEventListener('orientationchange', onOrientationChange);
      } else {
        window.removeEventListener('resize', handleResize);
      }
    }
      
    function handleResize() {
      const ORIGINAL_WIDTH = 800;
      const ORIGINAL_HEIGHT = 400;
      const margin = 12; // Marge interne utilisée pour le positionnement
      const container = document.querySelector('.game-container');
      if (!container) return;
  
      // Dimensions du conteneur et de la fenêtre
      const containerWidth = container.clientWidth;
      const windowHeight = window.innerHeight;
  
      // Calcul du scale en fonction de l'espace disponible
      let scale = Math.min(containerWidth / ORIGINAL_WIDTH, windowHeight * 0.7 / ORIGINAL_HEIGHT);
  
      // Appliquer le scale sur le canvas (dimension affichée)
      canvas.style.width = (ORIGINAL_WIDTH * scale) + 'px';
      canvas.style.height = (ORIGINAL_HEIGHT * scale) + 'px';
  
      // Garder la résolution logique du canvas inchangée
      canvas.width = ORIGINAL_WIDTH;
      canvas.height = ORIGINAL_HEIGHT;
      
      // Ajuster dynamiquement la hauteur du game-container (en fonction de la largeur)
      container.style.height = Math.min(windowHeight * 0.8, containerWidth / 2) + 'px';
  
      ctx.imageSmoothingEnabled = false;
  
      // Utilisation du facteur d'échelle pour d'autres ajustements
      const s = scale;
  
      // Positionnement absolu de score-display par rapport à game-container
      // On considère que :
      //   - Le canvas est positionné en absolute dans le game-container (déjà défini dans votre CSS).
      //   - Le canvas est décalé d'une marge (margin) par rapport au bord supérieur et gauche du container.
      // On positionne alors le score-display pour qu'il soit centré horizontalement sur le bord supérieur du canvas.
      const scoreDisplay = document.getElementById("score-display");
      if (scoreDisplay) {
          // Assurez-vous que le game-container est en position relative (pour que le positionnement absolu se fasse par rapport à lui)
          container.style.position = "relative";
          // Le canvas devrait être positionné en absolute (vérifiez votre CSS)
          // Récupérer la position du canvas par rapport au container (offsetLeft et offsetTop fonctionnent si le container est en position relative)
          const canvasLeft = canvas.offsetLeft;
          const canvasTop = canvas.offsetTop;
          // Calculer la largeur affichée du canvas (en pixels)
          const canvasDisplayWidth = ORIGINAL_WIDTH * s;
  
          // Placer le score-display centré sur le bord supérieur du canvas.
          // On fixe sa position verticale à la même valeur que canvasTop (souvent égale à la marge appliquée)
          // et sa position horizontale au centre du canvas.
          scoreDisplay.style.position = "absolute";
          scoreDisplay.style.left = (canvasLeft + canvasDisplayWidth / 2) + "px";
          scoreDisplay.style.top = (canvasTop + 2) + "px";
          // Pour centrer le score-display par rapport à son point de positionnement, on décale de 50% de sa largeur.
          scoreDisplay.style.transform = "translate(-50%, 0)";
          scoreDisplay.style.transformOrigin = "center top";
  
          // On fixe la taille de la police en pixels pour éviter les fluctuations liées aux unités rem
          scoreDisplay.style.fontSize = (30 * s) + "px";
      }
  }


  function handleresizeTactile() {
    // Dimensions internes du canvas (logique du jeu inchangée)
    const ORIGINAL_WIDTH = 800;   // Utilisé pour la hauteur du terrain (après rotation)
    const ORIGINAL_HEIGHT = 400;  // Utilisé pour la largeur du terrain (après rotation)
    const margin = 20;            // Marge interne dans la game-container
    const horizontalExtra = 2 * margin; // 40px au total
    const baseControlHeight = 100; // Hauteur de base des boutons pour s = 1

    // Pour le calcul vertical total, on tient compte de :
    // - La hauteur affichée du terrain : ORIGINAL_WIDTH * s + horizontalExtra
    // - La hauteur du conteneur des boutons : baseControlHeight * s
    // - Le padding vertical du conteneur principal (#livegame) : 20 top + 20 bottom = 40
    // - Une marge fixe entre terrain et boutons : 5px
    // Total vertical = 800*s + 40 + 100*s + 45 = 900*s + 85
    const verticalExtra = 85;

    // Pour le calcul horizontal, nous utilisons la largeur disponible dans la colonne Bootstrap.
    const parentCol = document.getElementById('game-col');
    const availableWidth = parentCol ? parentCol.clientWidth : window.innerWidth;

    // Calcul de l'échelle horizontal : la largeur affichée du terrain sera ORIGINAL_HEIGHT * s + horizontalExtra
    const s_h = (availableWidth - horizontalExtra) / ORIGINAL_HEIGHT;

    // Calcul de l'échelle vertical : l'espace total requis verticalement est 900*s + 85, qui doit tenir dans window.innerHeight.
    const s_v = (window.innerHeight - verticalExtra) / 900;

    // On prend le facteur le plus contraignant
    const computedS = Math.min(s_h, s_v);

    // Calcul de l'échelle minimale pour que le terrain ait au moins 100px de largeur et 200px de hauteur.
    const sMinWidth = (100 - horizontalExtra) / ORIGINAL_HEIGHT;   // (100 - 40)/400 = 0.15
    const sMinHeight = (200 - horizontalExtra) / ORIGINAL_WIDTH;    // (200 - 40)/800 = 0.2
    const sMin = Math.max(sMinWidth, sMinHeight); // ici sMin = 0.2

    // On s'assure que l'échelle ne descend pas en dessous de sMin.
    const s = Math.max(computedS, sMin);

    // Mise à jour des dimensions du game-container (terrain)
    const gameContainer = document.querySelector('.game-container');
    if (!gameContainer) {
      console.error("L'élément '.game-container' est introuvable dans le DOM.");
      return;
    }
    gameContainer.style.width = (ORIGINAL_HEIGHT * s + horizontalExtra) + "px"; // 400*s + 40
    gameContainer.style.height = (ORIGINAL_WIDTH * s + horizontalExtra) + "px";  // 800*s + 40

    // Transformation du canvas pour le rendre vertical :
    const canvas = document.getElementById('gameCanvas');
    canvas.style.transform =
      `translate(${margin}px, ${margin}px) translateY(${ORIGINAL_WIDTH * s}px) rotate(-90deg) scale(${s})`;

    // Mise à jour de la hauteur du conteneur des boutons (touch-controls) en fonction de l'échelle.
    const controls = document.getElementById('left_player');
    const controlHeight = baseControlHeight * s;
    if (controls) {
      controls.style.height = controlHeight + "px";
    }

    // Transmet l'échelle aux boutons via la variable CSS --btn-scale pour qu'ils se redimensionnent proportionnellement.
    document.documentElement.style.setProperty('--btn-scale', s);

    // Mise à jour de la position de la zone de score pour l'accrocher entre le bord du game-container et celui du canvas (sans rotation)
const scoreDisplay = document.getElementById("score-display");
if (scoreDisplay) {
    // On souhaite que le score soit positionné de sorte que son centre soit à mi-distance
    // entre le bord gauche du game-container (0) et le bord gauche du canvas (qui est à "margin" pixels)
    const posX = margin / 2;  // Ceci correspond au point milieu horizontal
    // Pour le centrage vertical, on se base sur la hauteur actuelle du game-container.
    const posY = gameContainer.clientHeight / 2;
    
    // Positionnement absolu dans le game-container :
    scoreDisplay.style.left = posX + "px";
    scoreDisplay.style.top = posY + "px";
    
    // Appliquer un translate(-50%, -50%) pour que le centre de la zone corresponde à ce point,
    // sans aucune rotation (le texte reste dans son orientation normale)
    scoreDisplay.style.transform = "translate(-50%, -50%)";
    scoreDisplay.style.transformOrigin = "center";
    
    // Adaptez la taille de la police en fonction du scale, pour qu'elle reste proportionnelle
    scoreDisplay.style.fontSize = (1.5 * s) + "rem";
}

}
  

// Seuil (en pixels) pour considérer qu'un glissement a eu lieu
const SWIPE_THRESHOLD = 50;
let touchStartY = null;

document.addEventListener('touchstart', (e) => {
  // Enregistrer la position verticale au début du toucher (si un seul doigt)
  if (e.touches.length === 1) {
    touchStartY = e.touches[0].clientY;
  }
}, { passive: true });

document.addEventListener('touchend', (e) => {
  if (touchStartY === null) return;
  const touchEndY = e.changedTouches[0].clientY;
  const deltaY = touchEndY - touchStartY;
  
  const navbar = document.getElementById('navbar');
  if (!navbar) return;

  // Si l'utilisateur glisse vers le bas (delta positif) et dépasse le seuil
  if (deltaY > SWIPE_THRESHOLD) {
    navbar.classList.remove('hidden');
    // Optionnel : masquer la navbar de nouveau après quelques secondes
    setTimeout(() => {
      // Vérifier que l'écran est toujours en paysage
      if (window.innerWidth > window.innerHeight) {
        navbar.classList.add('hidden');
      }
    }, 3000);
  }
  
  // Si l'utilisateur glisse vers le haut (delta négatif) et dépasse le seuil
  if (deltaY < -SWIPE_THRESHOLD) {
    navbar.classList.add('hidden');
  }
  
  // Réinitialiser la valeur
  touchStartY = null;
});

function adjustGlobalRotator() {
	const rotator = document.getElementById('global-rotator');
	if (!rotator) return;
	
	// Dans le cas d'une rotation forcée en portrait,
	// on définit la largeur et la hauteur en fonction des dimensions de l'écran.
	if (window.innerHeight > window.innerWidth) {
	  rotator.style.width = window.innerHeight + 'px';
	  rotator.style.height = window.innerWidth + 'px';
	  rotator.style.transform = 'rotate(90deg)';
	} else {
	  rotator.style.width = window.innerWidth + 'px';
	  rotator.style.height = window.innerHeight + 'px';
	  rotator.style.transform = 'none';
	}
  }
  
  window.addEventListener('resize', adjustGlobalRotator);
  window.addEventListener('orientationchange', adjustGlobalRotator);
  adjustGlobalRotator();

  
    // 4) Initialiser WebSocket
    const socket = new WebSocket(config.wsUrl);
    // stocker le socket pour pouvoir le disconnect en cas de changement de page dans la spa
    window.currentGameSocket = socket;
    
    socket.onopen = () => {
      console.log("[live_game_utils] WebSocket connection opened:", config.wsUrl);
      initializeTouchControls(config.userRole, socket);
    };
    socket.onclose = () => {
      console.log("[live_game_utils] WebSocket closed (maybe user left the page).");
      // Si ce n’est pas un "game_over", on résout quand même la promesse
      resolve(); 
    };
  
    // 5) Gérer l'état du jeu local
    const activeEffects = { left: new Set(), right: new Set() };
    const effectTimers = {};
    let gameState = {
      type: 'game_state',
      ball_x: 400, 
      ball_y: 200,
      ball_size: 7,
      ball_speed_x: 4,
      ball_speed_y: 4,
      paddle_left_y: 170,
      paddle_right_y: 170,
      paddle_width: 10,
      paddle_left_height: 60,
      paddle_right_height: 60,
      score_left: 0, 
      score_right: 0,
      powerups: [],
      bumpers: [],
      flash_effect: false
    };
	// let showCountdown = false;
    // let countdownNumber = 3;
  
    // 6) Gérer la réception de messages WebSocket
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
  
      if (data.type === 'game_state') {
        // Mémoriser les effets actifs avant maj
        const prevLeft = new Set(activeEffects.left);
        const prevRight = new Set(activeEffects.right);
        gameState = data;
        // Réinjecter
        activeEffects.left = prevLeft;
        activeEffects.right = prevRight;
      }  else if (data.type === 'powerup_spawned') {
		const powerupColor = {
			'invert': '#FF69B4',
			'shrink': '#FF0000',
			'ice': '#00FFFF',
			'speed': '#FFD700',
			'flash': '#FFFF00',
			'sticky': '#32CD32'
		}[data.powerup.type] || '#FFFFFF';
		
		createSpawnEffect('powerup_spawn', 
			data.powerup.x, 
			data.powerup.y, 
			data.powerup.type,
			powerupColor);
	  } else if (data.type === 'powerup_expired') {
		createSpawnEffect('powerup_expire',
			data.powerup.x,
			data.powerup.y,
			data.powerup.type);
		} else if (data.type === 'bumper_spawned') {
			createSpawnEffect('bumper_spawn',
				data.bumper.x,
				data.bumper.y);
			
		} else if (data.type === 'bumper_expired') {
			createSpawnEffect('bumper_expire',
				data.bumper.x,
				data.bumper.y);
    } else if (data.type === 'countdown') {
      // Stocker le compte à rebours dans le gameState
      gameState.countdown = data.countdown_nb;
      // drawCountdown(data.countdown_nb);
		} else if (data.type === 'collision_event') {
			const collision = data.collision;
			switch(collision.type) {
				case 'paddle_collision':
					createCollisionEffect('paddle_collision', 
						collision.paddle_side === 'left' ? 60 : canvas.width - 60, 
						gameState.ball_y);
					break;
					
				case 'border_collision':
					createCollisionEffect('border_collision',
						collision.coor_x_collision,
						collision.border_side === 'up' ? 50 : 350);
					break;
					
				case 'bumper_collision':
					createCollisionEffect('bumper_collision',
						collision.bumper_x,
						collision.bumper_y);
					break;
			}
		}
		else if (data.type === 'game_over') {
        console.log("[live_game_utils] Game over detected");
        // alert("Game Over! Winner = " + data.winner);
        socket.close();
        resolve();  // 🔹 Signale à `runTournamentFlow()` que la partie est terminée
      }
      else if (data.type === 'powerup_applied') {
        // console.log(`[live_game_utils] Power-up applied to ${data.player}: ${data.effect}`);
        if (data.effect === 'flash') {
          applyFlashEffect(gameState);
          return;
        }
        let displaySide = data.player;
        if (!['speed','sticky'].includes(data.effect)) {
          // Les autres s'appliquent à l'adversaire
          displaySide = (data.player === 'left') ? 'right' : 'left';
        }
        activeEffects[displaySide].add(data.effect);
  
        // Timer pour retirer l'effet
        if (effectTimers[`${displaySide}_${data.effect}`]) {
          clearTimeout(effectTimers[`${displaySide}_${data.effect}`]);
        }
        effectTimers[`${displaySide}_${data.effect}`] = setTimeout(() => {
          console.log(`[live_game_utils] Removing effect ${data.effect} for ${displaySide}`);
          activeEffects[displaySide].delete(data.effect);
        }, data.duration * 1000);
      }
    };
  
    // 7) Gérer le clavier et les touches tactiles
    function initializeTouchControls(userRole, socket) {
      // On active les contrôles tactiles uniquement si on est en mode tactile
      if (!isTouchDevice()) return; // Si pas tactile, on ne fait rien ici.
    
      // Gestion globale du double tap pour empêcher le zoom
      let lastTouchEnd = 0;
      document.addEventListener('touchend', function(e) {
        const now = Date.now();
        if (now - lastTouchEnd <= 300) {
          // Si deux touchend se succèdent rapidement, on annule l'action par défaut
          e.preventDefault();
        }
        lastTouchEnd = now;
      }, { passive: false });
    
      // Sélectionnez les boutons par leur id
      const btnUp = document.getElementById("touch1");
      const btnDown = document.getElementById("touch2");
    
      // Vérifiez que les boutons existent
      if (!btnUp || !btnDown) {
        console.error("Les boutons tactiles ne sont pas définis dans le DOM.");
        return;
      }
    
      // Pour le bouton "up"
      btnUp.addEventListener('touchstart', (e) => {
        e.preventDefault();
        socket.send(JSON.stringify({
          action: "start_move",
          player: userRole,
          direction: "up"
        }));
      });
      btnUp.addEventListener('touchend', (e) => {
        e.preventDefault();
        socket.send(JSON.stringify({
          action: "stop_move",
          player: userRole
        }));
      });
      // Optionnel pour le clic (au cas où)
      btnUp.addEventListener('click', (e) => {
        e.preventDefault();
        socket.send(JSON.stringify({
          action: "start_move",
          player: userRole,
          direction: "up"
        }));
        setTimeout(() => {
          socket.send(JSON.stringify({
            action: "stop_move",
            player: userRole
          }));
        }, 200);
      });
    
      // Pour le bouton "down"
      btnDown.addEventListener('touchstart', (e) => {
        e.preventDefault();
        socket.send(JSON.stringify({
          action: "start_move",
          player: userRole,
          direction: "down"
        }));
      });
      btnDown.addEventListener('touchend', (e) => {
        e.preventDefault();
        socket.send(JSON.stringify({
          action: "stop_move",
          player: userRole
        }));
      });
      btnDown.addEventListener('click', (e) => {
        e.preventDefault();
        socket.send(JSON.stringify({
          action: "start_move",
          player: userRole,
          direction: "down"
        }));
        setTimeout(() => {
          socket.send(JSON.stringify({
            action: "stop_move",
            player: userRole
          }));
        }, 200);
      });
    }    

    if (!isTouchDevice()) {
    const keysPressed = {};
  
    document.addEventListener('keydown', (evt) => {
      if (evt.repeat) return;
      let action = "start_move";
      let player = null, direction = null;
  

      if (config.userRole === 'both') {
        switch(evt.key) {
          case 'w':
          case 'W':
            player = 'left';
            direction = 'up';
            break;
          case 's':
          case 'S':
            player = 'left';
            direction = 'down';
            break;
          case 'ArrowUp':
            player = 'right';
            direction = 'up';
            break;
          case 'ArrowDown':
            player = 'right';
            direction = 'down';
            break;
        }
      }
	  else if (config.userRole === 'right') {
        switch(evt.key) {
			case 'ArrowUp':
			  player = 'right';
			  direction = 'up';
			  break;
			case 'ArrowDown':
			  player = 'right';
			  direction = 'down';
			  break;
		  }
      }
      else if (config.userRole === 'left') {
        switch(evt.key) {
          case 'ArrowUp':
            player = 'left';
            direction = 'up';
            break;
          case 'ArrowDown':
            player = 'left';
            direction = 'down';
            break;
        }
      }
  
      if (player && direction && !keysPressed[evt.key]) {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify({ action, player, direction }));
        }
        keysPressed[evt.key] = true;
        // console.log(`[live_game_utils] start_move: ${player}, ${direction}`);
      }
    });
  
    document.addEventListener('keyup', (evt) => {
      let action = "stop_move";
      let player = null;
  
      if (config.userRole === 'both') {
        if (['w','W','s','S'].includes(evt.key)) {
          player = 'left';
        }
      }
      
      if ((config.userRole === 'both' || config.userRole === 'right' || config.userRole === 'left') && !player) {
        if (['ArrowUp','ArrowDown'].includes(evt.key)) {
          if(config.userRole === 'both' || config.userRole === 'right')
		  	player = 'right';
		  else if(config.userRole === 'left')
		  	player = 'left';
        }
      }
  
      if (player && keysPressed[evt.key]) {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify({ action, player}));
        }
        keysPressed[evt.key] = false;
        // console.log(`[live_game_utils] stop_move: ${player}`);
      }
    });
  }


    
  
    // 8) Préparer les images powerups/bumper
    const powerupImages = {
      'invert': new Image(),
      'shrink': new Image(),
      'ice': new Image(),
      'speed': new Image(),
      'flash': new Image(),
      'sticky': new Image()
    };
    initPowerupImages(powerupImages);
  
    const bumperImage = new Image();
    bumperImage.src = createBumperSVG();


	// // -- Fonction pour démarrer la partie
  //   async function startGameWithCountdown(startGameBtn, onStartGame, gameId) {
	// 	showCountdown = true;
	// 	startGameBtn.classList.add('d-none');
		
	// 	// Start countdown animation
	// 	let count = 3;
		
	// 	// Function to update the countdown
  //   const updateCount = async () => {
	// 		countdownNumber = count;
	// 		count--;
			
	// 		if (count < 0) {
	// 			clearInterval(countdownInterval);
	// 			showCountdown = false;
	// 			// onStartGame && await onStartGame(gameId);
	// 		}
	// 	};
	
	// 	// Show first number immediately
	// 	updateCount();
		
	// 	// Then update every second
	// 	const countdownInterval = setInterval(updateCount, 1000);
	// }

  // async function displayCountdownNumber(countdown_nb, startGameBtn) {
	// 	showCountdown = true;
    
	// 	drawCountdown(countdown_nb)
		// Start countdown animation
		// let count = 3;
		
		// // Function to update the countdown
    // const updateCount = async () => {
		// 	countdownNumber = count;
		// 	count--;
			
		// 	if (count < 0) {
		// 		clearInterval(countdownInterval);
		// 		showCountdown = false;
		// 		// onStartGame && await onStartGame(gameId);
		// 	}
		// };
	
		// // Show first number immediately
		// updateCount();
		
		// // Then update every second
		// const countdownInterval = setInterval(updateCount, 1000);
	// }
  
    // 9) La boucle de dessin
    function draw() {
      if (gameState.flash_effect) {
        ctx.fillStyle = 'white';
        ctx.fillRect(0,0,canvas.width, canvas.height);
      } else {
        ctx.fillStyle = '#101A32';
        ctx.fillRect(0,0,canvas.width, canvas.height);
  
        // Zone de jeu
        ctx.strokeStyle = 'white';
        ctx.lineWidth = 2;
        ctx.strokeRect(50,50, canvas.width-100, canvas.height-100);
  
        // Dessin raquettes
        ['left','right'].forEach(side => {
          ctx.save();
          if (activeEffects[side].size > 0) {
            activeEffects[side].forEach(effect => {
              const glowColor = {
                'speed':'#FFD700','shrink':'#FF0000','ice':'#00FFFF',
                'sticky':'#32CD32','invert':'#FF69B4','flash':'#FFFF00'
              }[effect];
              ctx.shadowColor = glowColor;
              ctx.shadowBlur = 10 * scale;
            });
          }
          ctx.fillStyle = 'white';
          if (side==='left') {
            ctx.fillRect(50, gameState.paddle_left_y,
                        gameState.paddle_width, gameState.paddle_left_height);
          } else {
            ctx.fillRect(canvas.width-50 - gameState.paddle_width, 
                        gameState.paddle_right_y,
                        gameState.paddle_width, gameState.paddle_right_height);
          }
          ctx.restore();
        });
  
        // Balle
        ctx.fillStyle = 'white';
        ctx.beginPath();
        ctx.arc(gameState.ball_x, gameState.ball_y, gameState.ball_size, 0, 2*Math.PI);
        ctx.fill();
  
        // Powerups
        gameState.powerups.forEach(orb => {
          const type = orb.type || 'speed';
          const img = powerupImages[type];
          if (img.complete) {
            ctx.save();
            const glowColors = {
              'invert':'#FF69B4','shrink':'#FF0000','ice':'#00FFFF',
              'speed':'#FFD700','flash':'#FFFF00','sticky':'#32CD32'
            };
            ctx.shadowColor = glowColors[type] || '#FFD700';
            ctx.shadowBlur = 10 * scale;
            ctx.drawImage(img, orb.x - 15, orb.y - 15, 30, 30);
            ctx.restore();
          }
        });
  
        // Bumpers
        gameState.bumpers.forEach(bmp => {
          if (bumperImage.complete) {
            ctx.save();
            ctx.shadowColor = '#4169E1';
            ctx.shadowBlur = 10 * scale;
            ctx.drawImage(bumperImage,
              bmp.x - bmp.size, bmp.y - bmp.size,
              bmp.size*2, bmp.size*2
            );
            ctx.restore();
          }
        });
      }
  
      // Scores
      // ctx.fillStyle = 'white';
      // ctx.font = '20px Arial';
      // ctx.fillText(""+ gameState.score_left, 20, 30);
      // ctx.fillText(""+ gameState.score_right, canvas.width-40, 30);
      
      function updateScoreDisplay() {
        const scoreEl = document.getElementById("score-nb");
        if (scoreEl) {
          // Ici, on suppose que les noms sont déjà injectés via Django dans le HTML.
          // Par exemple, on pourrait avoir utilisé des attributs data pour conserver ces noms.
          // Si ce n'est pas le cas, vous pouvez également définir des variables globales injectées par Django.
          // Ici, nous allons lire le texte initial et remplacer uniquement la partie numérique.
          // Pour plus de flexibilité, vous pouvez modifier cette fonction selon vos besoins.
          // Exemple avec des attributs data (optionnel) :
          scoreEl.innerText = ` ${gameState.score_left} - ${gameState.score_right} `;
        }
        }

      // Affichage powerups actifs
      const powerupNames = {
        'speed':'SPEED','shrink':'SHRINK','ice':'ICE','sticky':'STICKY','invert':'INVERT'
      };
      // Gauche
      if (activeEffects.left.size > 0) {
        ctx.font='16px Arial';
        let yOffset=60;
        activeEffects.left.forEach(effect => {
          ctx.fillStyle = {
            'speed':'#FFD700','shrink':'#FF0000','ice':'#00FFFF',
            'sticky':'#32CD32','invert':'#FF69B4','flash':'#FFFF00'
          }[effect];
          ctx.fillText(powerupNames[effect], 20, yOffset);
          yOffset+=25;
        });
      }
      // Droite
      if (activeEffects.right.size > 0) {
        ctx.font='16px Arial';
        let yOffset=60;
        activeEffects.right.forEach(effect => {
          ctx.fillStyle = {
            'speed':'#FFD700','shrink':'#FF0000','ice':'#00FFFF',
            'sticky':'#32CD32','invert':'#FF69B4','flash':'#FFFF00'
          }[effect];
          const tW = ctx.measureText(powerupNames[effect]).width;
          ctx.fillText(powerupNames[effect], canvas.width-20 - tW, yOffset);
          yOffset+=25;
        });
      }
    updateScoreDisplay();
	  drawCollisionEffects();
	  drawCountdown();
      requestAnimationFrame(draw);
    }
    requestAnimationFrame(draw);
  
    // on peut retourner un objet si on veut
    return {
      socket,
      getGameState: () => gameState
    };
  });
}
  