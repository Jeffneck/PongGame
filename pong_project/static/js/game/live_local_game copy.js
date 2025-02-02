import { requestPost }  from '../api/index.js';


/**
 * Initialise le jeu local en direct (live local game).
 * @param {Object} options - Options nécessaires pour le jeu.
 * @param {string} options.gameId - L'ID de la partie.
 * @param {string} [options.csrfToken] - Le token CSRF si nécessaire pour les requêtes POST.
 * @param {string} [options.resultsUrl] - URL de redirection en cas de fin de partie.
 */
export function liveLocalGame(options) {
    const {
      gameId,
      resultsUrl = '/results' // Par défaut, on redirige vers /results
    } = options;
  
    // -- Récupérer les éléments HTML injectés
    const gameTitleEl = document.getElementById('game-id');
    const startGameBtn = document.getElementById('startGameBtn');
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
  
    // Mettre à jour l'affichage de l'ID du jeu
    if (gameTitleEl) {
      gameTitleEl.textContent = gameId;
    }
  
	// Rendre le bouton invisible et sans halo au début

    // -- Débloquer le bouton après 3 secondes (logique front)
    setTimeout(() => {
      if (startGameBtn) {
		startGameBtn.style.opacity = "0.7";
        startGameBtn.disabled = false;
		startGameBtn.classList.add("active");
      }
    }, 3000);
  
    // -- Fonction pour démarrer la partie
    async function startGame() {
      showCountdown = true;
      startGameBtn.classList.add('d-none');
      
      // Start countdown animation
      let count = 3;
      
      // Function to update the countdown
      const updateCount = () => {
          countdownNumber = count;
          count--;
          
          if (count < 0) {
              clearInterval(countdownInterval);
              showCountdown = false;
              sendStartGameRequest();
          }
      };
  
      // Show first number immediately
      updateCount();
      
      // Then update every second
      const countdownInterval = setInterval(updateCount, 1000);
  }
  
  async function sendStartGameRequest() {
      const url = `start_local_game/${gameId}`  // Define url here
      const formData = new FormData();
      formData.append('game_id', gameId);
      const response = await requestPost('game', url, formData);
      console.log(`[FRONTEND] Debug startGame response ${response}`);
      
      if (response.status !== 'success') {
          alert("Erreur lors du démarrage de la partie : " + response.message);
      }
  }

    // Attacher l'événement au bouton
    if (startGameBtn) {
      startGameBtn.addEventListener('click', startGame);
    }
  
    // -- Mise en place de la logique de redimensionnement du canvas
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
    if (showCountdown) {
        // Save context state
        ctx.save();
        
        // Add semi-transparent overlay
        ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Draw countdown number
        ctx.fillStyle = 'white';
        ctx.font = 'bold 80px Arial';  // Reduced from 120px to 80px
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        // Add glow effect
        ctx.shadowColor = 'rgba(255, 255, 255, 0.8)';
        ctx.shadowBlur = 20;
        
        // Position in center of canvas but higher up
        // Changed from canvas.height / 2 to canvas.height / 3 to move it up
        ctx.fillText(countdownNumber, canvas.width / 2, canvas.height / 3);
        
        // Restore context state
        ctx.restore();
    }
}

function handleResize() {
    const container = document.querySelector('.game-container');
    if (!container) return;

    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;
    const windowHeight = window.innerHeight; // Récupère la hauteur de l'écran

    // Calcul du scale basé sur la hauteur de l'écran
    let scale = Math.min(containerWidth / ORIGINAL_WIDTH, windowHeight * 0.7 / ORIGINAL_HEIGHT);

    // Appliquer le scale sans dépasser la hauteur disponible
    canvas.style.width = (ORIGINAL_WIDTH * scale) + 'px';
    canvas.style.height = (ORIGINAL_HEIGHT * scale) + 'px';

    // Garder la résolution nette
    canvas.width = ORIGINAL_WIDTH;
    canvas.height = ORIGINAL_HEIGHT;
    
    // Ajuster dynamiquement la hauteur de .game-container
    container.style.height = Math.min(windowHeight * 0.8, containerWidth / 2) + 'px';

    ctx.imageSmoothingEnabled = false;
}

window.addEventListener('resize', handleResize);
handleResize(); // Appel initial
  
    // -- Configuration WebSocket
    const protocol = (window.location.protocol === 'https:') ? 'wss:' : 'ws:';
    const wsUrl = protocol + '//' + window.location.host + '/ws/pong/' + gameId + '/';
    const socket = new WebSocket(wsUrl);
  
    // -- Gestion des effets actifs
    const activeEffects = {
      left: new Set(),
      right: new Set()
    };
    const effectTimers = {};
  
    // -- État du jeu côté client
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
    let showCountdown = false;
    let countdownNumber = 3;

    socket.onopen = () => {
      console.log("[Frontend] WebSocket connection opened.");
    };
  
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch(data.type) {
          case 'game_state':
              const oldScoreLeft = gameState.score_left;
              const oldScoreRight = gameState.score_right;
              
              // Update game state
              gameState = data;
              
              // Check if a point was scored by comparing old and new scores
              if (gameState.score_left !== oldScoreLeft || gameState.score_right !== oldScoreRight) {
                  // Clear all active effects
                  activeEffects.left = new Set();
                  activeEffects.right = new Set();
                  
                  // Cancel all pending effect timers
                  Object.keys(effectTimers).forEach(key => {
                      clearTimeout(effectTimers[key]);
                      delete effectTimers[key];
                  });
                  
                  // Clear powerups array
                  gameState.powerups = [];
                  gameState.bumpers = [];
                  gameState.flash_effect = false;
          
                  // Force a redraw to clear any lingering visual effects
                  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
                  console.log("[Frontend] Reset all effects after point scored");
              }
              break;
  
          case 'powerup_spawned':
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
              break;
  
          case 'powerup_expired':
              createSpawnEffect('powerup_expire',
                  data.powerup.x,
                  data.powerup.y,
                  data.powerup.type);
              break;
  
          case 'bumper_spawned':
              createSpawnEffect('bumper_spawn',
                  data.bumper.x,
                  data.bumper.y);
              break;
  
          case 'bumper_expired':
              createSpawnEffect('bumper_expire',
                  data.bumper.x,
                  data.bumper.y);
              break;
  
          case 'collision_event':
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
              break;
  
          case 'powerup_applied':
              console.log(`[Frontend] Power-up applied to ${data.player}: ${data.effect}`);
              console.log(`[Frontend] Power-up duration: ${data.duration}`);
              
              if (data.effect !== 'flash') {
                  let displaySide;
                  if (data.effect === 'speed' || data.effect === 'sticky') {
                      // Speed and sticky show on the side that picked it up
                      displaySide = data.player;
                  } else {
                      // Other effects show on the opponent's side
                      displaySide = data.player === 'left' ? 'right' : 'left';
                  }
                  
                  // Add effect to active effects
                  activeEffects[displaySide].add(data.effect);
                  console.log("Active effects immediately after adding:", {
                      left: Array.from(activeEffects.left),
                      right: Array.from(activeEffects.right)
                  });
                  
                  // Clear previous timer if it exists
                  if (effectTimers[`${displaySide}_${data.effect}`]) {
                      clearTimeout(effectTimers[`${displaySide}_${data.effect}`]);
                  }
                  
                  // Set timer to remove effect
                  effectTimers[`${displaySide}_${data.effect}`] = setTimeout(() => {
                      console.log(`[Frontend] Removing effect ${data.effect} for ${displaySide}`);
                      activeEffects[displaySide].delete(data.effect);
                      console.log("Active effects after removal:", {
                          left: Array.from(activeEffects.left),
                          right: Array.from(activeEffects.right)
                      });
                  }, data.duration * 1000);
              } else {
                  applyFlashEffect();
              }
              break;
  
          case 'game_over':
              // Clear all effects on game over too
              activeEffects.left.clear();
              activeEffects.right.clear();
              console.log(`[Frontend] Game over detected`);
              Object.keys(effectTimers).forEach(key => {
                  clearTimeout(effectTimers[key]);
                  delete effectTimers[key];
              });
              
              alert("Game Over! Winner = " + data.winner);
              socket.close();
              window.location.href = resultsUrl;
              break;
      }
    };

    socket.onclose = () => {
      console.log("[Frontend] WebSocket connection closed.");
    };
  
    // -- Gestion du clavier pour le mouvement des raquettes
    let keysPressed = {};
  
    document.addEventListener('keydown', (evt) => {
      if (evt.repeat) return; // évite le spam
      
      let action = "start_move", player = null, direction = null;
      
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
      if (player && direction && !keysPressed[evt.key]) {
        socket.send(JSON.stringify({
          action: action,
          player: player,
          direction: direction
        }));
        console.log(`[Frontend] Sent start_move: player=${player}, direction=${direction}`);
        keysPressed[evt.key] = true;
      }
    });
  
    document.addEventListener('keyup', (evt) => {
      let action = "stop_move", player = null;
  
      switch(evt.key) {
        case 'w':
        case 'W':
        case 's':
        case 'S':
          player = 'left';
          break;
        case 'ArrowUp':
        case 'ArrowDown':
          player = 'right';
          break;
      }
      if (player && keysPressed[evt.key]) {
        socket.send(JSON.stringify({
          action: action,
          player: player
        }));
        console.log(`[Frontend] Sent stop_move: player=${player}`);
        keysPressed[evt.key] = false;
      }
    });
  

// Dossier où sont stockés les fichiers SVG dans le dossier static/ de Django
const SVG_FOLDER = '/static/svg/';

const powerupImages = {};
const bumperImage = new Image();

function preloadImages() {
    const types = ['invert', 'shrink', 'ice', 'speed', 'flash', 'sticky'];
    let loaded = 0;

    return new Promise((resolve) => {
        types.forEach(type => {
            const img = new Image();
            img.onload = () => {
                loaded++;
                if (loaded === types.length + 1) resolve();
            };
            img.src = `${SVG_FOLDER}${type}.svg`;
            powerupImages[type] = img;
        });

        // Charger le bumper
        bumperImage.onload = () => {
            loaded++;
            if (loaded === types.length + 1) resolve();
        };
        bumperImage.src = `${SVG_FOLDER}bumper.svg`;
    });
}

  
    // Effet flash
    function applyFlashEffect() {
      gameState.flash_effect = true;
      setTimeout(() => {
        gameState.flash_effect = false;
      }, 300);  // 300 ms
    }
  
    // -- Fonction de dessin sur le canvas
    function draw() { //added
      // console.log("Active Effects:", activeEffects);
      if (gameState.flash_effect) {
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      } else {
        ctx.fillStyle = '#101A32'; // Changer la couleur de fond en bleu
        ctx.fillRect(0, 0, canvas.width, canvas.height);
	
        
        // Terrain
        ctx.strokeStyle = 'white';
        ctx.lineWidth = 2;
        ctx.strokeRect(50, 50, canvas.width - 100, canvas.height - 100);
        
        // Paddles with effects
        ['left', 'right'].forEach(side => {
          ctx.save();
          
          // Add effect glows added
          if (activeEffects[side].size > 0) {
            activeEffects[side].forEach(effect => {
              const glowColor = {
                'speed': '#FFD700',
                'shrink': '#FF0000',
                'ice': '#00FFFF',
                'sticky': '#32CD32',
                'invert': '#FF69B4'
              }[effect];
              ctx.shadowColor = glowColor;
              ctx.shadowBlur = 10 * scale;
            });
          }
          
          ctx.fillStyle = 'white';
          if (side === 'left') {
            ctx.fillRect(50, gameState.paddle_left_y,
              gameState.paddle_width, gameState.paddle_left_height);
          } else {
            ctx.fillRect(canvas.width - 50 - gameState.paddle_width,
              gameState.paddle_right_y,
              gameState.paddle_width, gameState.paddle_right_height);
          }
          
          ctx.restore();
        });
        
        // Ball
        ctx.fillStyle = 'white';
        ctx.beginPath();
        ctx.arc(gameState.ball_x, gameState.ball_y, gameState.ball_size, 0, 2*Math.PI);
        ctx.fill();

        // Power-ups
        // Dessiner les Power-ups avec les fichiers SVG
		gameState.powerups.forEach(orb => {
			const type = orb.type || 'speed';
			const img = powerupImages[type];
		
			if (img.complete) {
			ctx.save();
			ctx.drawImage(img, orb.x - 15, orb.y - 15, 30, 30);
			ctx.restore();
			}
		});
		
		// Dessiner les Bumpers avec le fichier SVG
		gameState.bumpers.forEach(bumper => {
			if (bumperImage.complete) {
			ctx.save();
			ctx.drawImage(bumperImage, bumper.x - bumper.size, bumper.y - bumper.size, bumper.size * 2, bumper.size * 2);
			ctx.restore();
			}
		});
  
  
        // Bumpers
      }

  
      // Scores
      ctx.fillStyle = 'white';
      ctx.font = "20px Arial";
      ctx.fillText(`${gameState.score_left}`, 20, 30);
      ctx.fillText(`${gameState.score_right}`, canvas.width - 40, 30);

	  
  
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
        ctx.font = "16px Arial";
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
          yOffset += 25;
        });
      }
  
      // Droite
      if (activeEffects.right.size > 0) {
        ctx.font = "16px Arial";
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
          yOffset += 25;
        });
      }
      drawCollisionEffects();
      drawCountdown();
      requestAnimationFrame(draw);
    }
  
    // // Lancer la boucle de rendu
    // requestAnimationFrame(draw);
	preloadImages().then(() => {
		console.log("[Frontend] Images SVG chargées, démarrage du jeu...");
		requestAnimationFrame(draw);
	});
  }
  