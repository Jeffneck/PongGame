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
import { isTouchDevice } from '../tools/utility.js';


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
        return; 
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
	// Masquer les boutons tactiles si l'appareil n'est pas tactile.
    if (!isTouchDevice()) {
		const touchControls = document.querySelector('.touch-controls');
		if (touchControls) {
		  // Ici, on masque simplement l'élément
		  touchControls.style.display = 'none';
		}
	  }
    // 1) Préparer les éléments HTML
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const startGameBtn = config.startGameSelector;
    console.log("Appareil tactile ?", isTouchDevice());
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
	// ===========================
  //  Function drawCollisionEffects
  // ===========================
  function drawCollisionEffects() {
    collisionEffects.forEach(effect => {
      // Calcul de l'âge de l'effet
      const now = Date.now();
      const age = now - effect.startTime;

      // Durée selon le type "spawn" ou "expire"
      const duration = effect.type.includes('spawn')
        ? SPAWN_EFFECT_DURATION
        : EXPIRE_EFFECT_DURATION;
      
      // progress brut
      const rawProgress = age / duration;
      // progress clampé entre 0 et 1
      const progress = Math.max(0, Math.min(rawProgress, 1));

      // Sauvegarde du contexte
      ctx.save();

      // On réduit l'alpha en fonction du progress
      ctx.globalAlpha = Math.max(0, 1 - progress);

      switch(effect.type) {

        case 'paddle_collision': {
          // Ripple effect
          const rippleSize = Math.max(0, 20 + (progress * 40));
          ctx.strokeStyle = 'white';
          ctx.lineWidth = 3 * (1 - progress);

          ctx.beginPath();
          ctx.arc(effect.x, effect.y, rippleSize, 0, Math.PI * 2);
          ctx.stroke();
          break;
        }

        case 'bumper_collision': {
          // Explosion effect
          const numParticles = 8;
          // on clamp pour éviter radius négatif
          const radius = Math.max(0, 30 * progress);

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
        }

        case 'powerup_spawn': {
          // Expanding circles with powerup color
          ctx.strokeStyle = effect.color;
          ctx.lineWidth = 2;

          const circles = 3;
          for (let i = 0; i < circles; i++) {
            // On modifie légèrement progress pour chaque cercle
            const circleProgress = (progress + (i / circles)) % 1;
            const radius = Math.max(0, circleProgress * 40);

            ctx.beginPath();
            ctx.arc(effect.x, effect.y, radius, 0, Math.PI * 2);
            ctx.stroke();
          }

          // Add sparkles
          const sparkles = 8;
          for (let i = 0; i < sparkles; i++) {
            const angle = (i / sparkles) * Math.PI * 2;
            // clamp pour éviter tout souci
            const sparkleDistance = Math.max(0, 20 + (progress * 20));

            const x = effect.x + Math.cos(angle) * sparkleDistance;
            const y = effect.y + Math.sin(angle) * sparkleDistance;
            
            ctx.beginPath();
            ctx.arc(x, y, 2, 0, Math.PI * 2);
            ctx.fillStyle = effect.color;
            ctx.fill();
          }
          break;
        }

        case 'powerup_expire': {
          // Imploding effect
          const fadeRadius = Math.max(0, 20 * (1 - progress));
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
            const distance = fadeRadius * 2; // base de départ
            const x = effect.x + Math.cos(angle) * distance * progress;
            const y = effect.y + Math.sin(angle) * distance * progress;

            ctx.beginPath();
            ctx.arc(x, y, 2, 0, Math.PI * 2);
            ctx.fill();
          }
          break;
        }

        case 'bumper_spawn': {
          // Expanding diamond pattern
          ctx.strokeStyle = '#4169E1';
          ctx.lineWidth = 2;
          const size = Math.max(0, 40 * progress);
          const rotation = progress * Math.PI;

          // On translate/rotate le contexte avant de dessiner
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
        }

        case 'bumper_expire': {
          // Dissolving rings effect
          ctx.strokeStyle = '#4169E1';
          ctx.lineWidth = 2 * (1 - progress);

          const rings = 3;
          for (let i = 0; i < rings; i++) {
            const ringProgress = (progress + (i / rings)) % 1;
            const ringRadius = Math.max(0, 20 * ringProgress);

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

  function drawScored() {
    if (typeof gameState.scoreMsg !== 'undefined') {
      ctx.save();
      ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
  
      ctx.fillStyle = 'yellow';
      ctx.font = 'bold 80px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.shadowColor = 'rgba(255, 255, 0, 0.8)';
      ctx.shadowBlur = 20;
      ctx.fillText(gameState.scoreMsg, canvas.width / 2, canvas.height / 3);
      ctx.restore();
    }
	}
  
    // 3) Mise en place du redimensionnement du canvas
    const ORIGINAL_WIDTH = 800;
    const ORIGINAL_HEIGHT = 400;
    let scale = 1;

	    // Const for visual effects on notifications /
		const collisionEffects = [];
		const EFFECT_DURATION = 300;
		const SPAWN_EFFECT_DURATION = 500;
		const EXPIRE_EFFECT_DURATION = 300;
	  
		// spawn visual effect 
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
	
	  // collision visual effects
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

    
      
   
  
	  function handleResize() {
		const ORIGINAL_WIDTH = 800;
		const ORIGINAL_HEIGHT = 400;
		const margin = 12; // Marge interne utilisée pour le positionnement
	  
		const canvas = document.getElementById('gameCanvas');
		if (!canvas) return;
		const ctx = canvas.getContext('2d');
	  
		// On récupère le conteneur de jeu (dans #livegame)
		const container = document.querySelector('.game-container');
		if (!container) return;
	  
		// Dimensions du conteneur et de la fenêtre
		const containerWidth = container.clientWidth;
		const windowHeight = window.innerHeight;
	  
		// Calcul du scale en fonction de l'espace disponible
		let scale = Math.min(containerWidth / ORIGINAL_WIDTH, windowHeight * 0.7 / ORIGINAL_HEIGHT);
	  
		// Mise à jour de la hauteur du conteneur des boutons (touch-controls)
		const touchControls = document.querySelector('.touch-controls');
		if (touchControls) {
		  // On définit temporairement la hauteur en fonction du scale (pour le mode horizontal)
		  touchControls.style.height = (ORIGINAL_HEIGHT * scale) + 'px';
		}
	  
		// Appliquer le scale sur le canvas (dimension affichée)
		canvas.style.width = (ORIGINAL_WIDTH * scale) + 'px';
		canvas.style.height = (ORIGINAL_HEIGHT * scale) + 'px';
		// Garder la résolution logique du canvas inchangée
		canvas.width = ORIGINAL_WIDTH;
		canvas.height = ORIGINAL_HEIGHT;
	  
		// Ajuster dynamiquement la hauteur du game-container
		container.style.height = Math.min(windowHeight * 0.8, containerWidth / 2) + 'px';
	  
		ctx.imageSmoothingEnabled = false;
		const s = scale;
	  
		// Positionnement du score-display par rapport au game-container
		const scoreDisplay = document.getElementById("score-display");
		if (scoreDisplay) {
		  container.style.position = "relative"; // S'assurer que le container est positionné en relatif
		  const canvasLeft = canvas.offsetLeft;
		  const canvasTop = canvas.offsetTop;
		  const canvasDisplayWidth = ORIGINAL_WIDTH * s;
		  scoreDisplay.style.position = "absolute";
		  scoreDisplay.style.left = (canvasLeft + canvasDisplayWidth / 2) + "px";
		  scoreDisplay.style.top = (canvasTop + 2) + "px";
		  scoreDisplay.style.transform = "translate(-50%, 0)";
		  scoreDisplay.style.transformOrigin = "center top";
		  scoreDisplay.style.fontSize = (30 * s) + "px";
		}
	  
		// --- Sélection du layout en fonction de l'orientation ---
		if (isTouchDevice() && window.innerWidth < window.innerHeight) {
			const livegame = document.getElementById("livegame");
			if (livegame) {
			  livegame.classList.add("rotate90");
			  // Appliquer les styles pour le mode vertical sur tactile
			  livegame.style.display = "flex";
			  // On laisse livegame en disposition normale (pas de flex-column ici, puisque les boutons seront dans .game-container)
			  // On impose que livegame occupe toute la hauteur de la fenêtre
			  livegame.style.height = window.innerHeight + "px";
			  // On fixe sa largeur à 100vh (correspondant à la hauteur de la fenêtre)
			  livegame.style.width = "100vh";
		  
			  // Ajuster le conteneur de jeu interne
			  const innerContainer = livegame.querySelector(".game-container");
			  if (innerContainer) {
				innerContainer.style.display = "flex";
				innerContainer.style.flexDirection = "column"; // Empile le canvas et les boutons verticalement
				innerContainer.style.alignItems = "center";
				innerContainer.style.justifyContent = "center";
				innerContainer.style.maxHeight = "90%";
				innerContainer.style.width = "85%";
				// innerContainer.style.width = "85%";
				innerContainer.style.margin = "auto";
				innerContainer.style.marginLeft = "0";
				innerContainer.style.left = "4%";


			  }

				// Pour garantir que le canvas garde toujours son ratio 2:1,
				// on calcule le scale comme d'habitude, puis on impose une hauteur minimale.
				const ORIGINAL_WIDTH = 800;
				const ORIGINAL_HEIGHT = 400;
				const containerWidth = innerContainer ? innerContainer.clientWidth : window.innerWidth;
				let scale = Math.min(containerWidth / ORIGINAL_WIDTH, window.innerWidth * 0.8 / ORIGINAL_HEIGHT);
				const minCanvasHeight = 100; // Hauteur minimale désirée
				if ((ORIGINAL_HEIGHT * scale) < minCanvasHeight) {
				scale = minCanvasHeight / ORIGINAL_HEIGHT;
				}
				// Appliquer le scale au canvas
				const canvas = document.getElementById('gameCanvas');
				canvas.style.width = (ORIGINAL_WIDTH * scale) + 'px';
				canvas.style.height = (ORIGINAL_HEIGHT * scale) + 'px';
				canvas.width = ORIGINAL_WIDTH;
				canvas.height = ORIGINAL_HEIGHT;
				
				// Ajuster le score-display (en se basant sur le canvas et le scale)
				const scoreDisplay = document.getElementById("score-display");
				if (scoreDisplay) {
				innerContainer.style.position = "relative";
				const canvasLeft = canvas.offsetLeft;
				const canvasTop = canvas.offsetTop;
				const canvasDisplayWidth = ORIGINAL_WIDTH * scale;
				scoreDisplay.style.position = "absolute";
				scoreDisplay.style.left = (canvasLeft + canvasDisplayWidth / 2) + "px";
				scoreDisplay.style.top = (canvasTop + 2) + "px";
				scoreDisplay.style.transform = "translate(-50%, 0)";
				scoreDisplay.style.transformOrigin = "center top";
				// On peut utiliser clamp() pour une taille de police adaptative
				scoreDisplay.style.fontSize = `clamp(16px, ${30 * scale}px, 30px)`;
				}
		  
			  // Dans ce mode, on veut que les boutons se placent sous le canvas
			  const touchControls = livegame.querySelector(".touch-controls");
			  if (touchControls) {
				// On retire toute propriété de position absolue pour laisser la disposition en flux (flow)
				touchControls.style.position = "static";
				// Ajouter une marge supérieure pour séparer le canvas des boutons
				touchControls.style.marginTop = "auto";
				// Calculer la largeur du canvas afin de fixer la largeur des boutons
				const canvasRect = canvas.getBoundingClientRect();
				// Ici, on fixe la largeur du conteneur des boutons à 0.02 fois la largeur du canvas
				touchControls.style.width = (canvasRect.width * 0.1) + "px";

				touchControls.style.marginLeft = (canvasRect.width * 2.15) + "px";
			  }
			}
		  }		   else if ((touchControls && getComputedStyle(touchControls).display !== "none")|| (isTouchDevice() && window.innerWidth > window.innerHeight)) {
		  // Mode horizontal ou appareil non tactile
		  // On retire les styles spécifiques au mode vertical, le cas échéant.
		  const livegame = document.getElementById("livegame");
		  if (livegame) {
			livegame.classList.remove("rotate90");
			livegame.style.height = "100%";
			livegame.style.width = "100%";
		  }
		  
		  if (touchControls) {
			// On réapplique la logique de positionnement relative au canvas
			const canvasRect = canvas.getBoundingClientRect();
			const containerRect = container.getBoundingClientRect();
			const gap = canvasRect.width * 0.01;
			const relativeCanvasRight = canvasRect.right - containerRect.left;
			touchControls.style.position = 'absolute';
			touchControls.style.left = (relativeCanvasRight + gap) + 'px';
			const relativeCanvasTop = canvasRect.top - containerRect.top;
			touchControls.style.top = relativeCanvasTop + 'px';
			touchControls.style.height = canvasRect.height + 'px';
			touchControls.style.width = (canvasRect.width * 0.07) + 'px';
			touchControls.style.marginLeft = "0px";
		  }
		}
	  }
	  
	  window.addEventListener('resize', handleResize);
	  window.addEventListener('load', handleResize);
	  handleResize();
	  




  
if (isTouchDevice()) {
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
  }
  
    // 4) Initialiser WebSocket
    const socket = new WebSocket(config.wsUrl);
    // stocker le socket pour pouvoir le disconnect en cas de changement de page dans la spa
    window.currentGameSocket = socket;
    
    socket.onopen = () => {
      console.log("[live_game_utils] WebSocket connection opened:", config.wsUrl);
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
    } else if (data.type === 'scored') {
        // Stocker le compte à rebours dans le gameState
        gameState.scoreMsg = data.scoreMsg;
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
  
    // 7) Gérer le clavier : en fonction de userRole
    const keysPressed = {};
  
    document.addEventListener('keydown', (evt) => {
		if (evt.key === "ArrowUp" || evt.key === "ArrowDown") { // eviter le scroll fleche (marche bien sur chrome et firefox)
		evt.preventDefault();
		}
      if (evt.repeat) return;
      let action = "start_move";
      let player = null, direction = null;
  
      // userRole = 'both' => local => on écoute W/S + flèches
      // userRole = 'left' => seulement W/S
      // userRole = 'right' => seulement flèches ↑/↓
      if (config.userRole === 'both' || config.userRole === 'left') {
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
        }
      }
      if ((config.userRole === 'both' || config.userRole === 'right') && !player) {
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
  
      // userRole=both/left => check W,S
      if (config.userRole === 'both' || config.userRole === 'left') {
        if (['w','W','s','S'].includes(evt.key)) {
          player = 'left';
        }
      }
      // userRole=both/right => check ArrowUp, ArrowDown
      if ((config.userRole === 'both' || config.userRole === 'right') && !player) {
        if (['ArrowUp','ArrowDown'].includes(evt.key)) {
          player = 'right';
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

      // Affichage des noms de power-up actifs
      const powerupNames = {
        'speed': 'SPEED',
        'shrink': 'SHRINK',
        'ice': 'ICE',
        'sticky': 'STICKY',
        'invert': 'INVERT'
      };
  
      // Gauche
      if (activeEffects.left.size > 0) {
        ctx.font = "bold 25px Arial";
        let yOffset = 60; 
        activeEffects.left.forEach(effect => {
          ctx.fillStyle = {
            'speed': '#FFD700',
            'shrink': '#FF0000',
            'ice': '#00FFFF',
            'sticky': '#32CD32',
            'invert': '#FF69B4',
            'flash': '#FFFF00'
          }[effect];
          ctx.fillText(powerupNames[effect], 20, yOffset);
          yOffset += 20;
        });
      }
  
      // Droite
      if (activeEffects.right.size > 0) {
        ctx.font = "bold 25px Arial";
        let yOffset = 60;
        activeEffects.right.forEach(effect => {
          ctx.fillStyle = {
            'speed': '#FFD700',
            'shrink': '#FF0000',
            'ice': '#00FFFF',
            'sticky': '#32CD32',
            'invert': '#FF69B4',
            'flash': '#FFFF00'
          }[effect];
          const textWidth = ctx.measureText(powerupNames[effect]).width;
          ctx.fillText(powerupNames[effect], canvas.width - 20 - textWidth, yOffset);
          yOffset += 20;
        });
      }
    updateScoreDisplay();
	  drawCollisionEffects();
	  drawCountdown();
	  drawScored();
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
  