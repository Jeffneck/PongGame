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
  
    // -- Débloquer le bouton après 3 secondes (logique front)
    setTimeout(() => {
      if (startGameBtn) {
        startGameBtn.disabled = false;
      }
    }, 3000);
  
    // -- Fonction pour démarrer la partie
    async function startGame() {
      const url = `start_local_game/${gameId}`
      // Envoie une requête au backend pour lancer la partie
      const formData = new FormData();
      formData.append('game_id', gameId)
      const response = await requestPost('game', url, formData) // IMPROVE, le form ne contient que gameId qui est aussi dans l'url = inutile ?
      console.log(`[FRONTEND] Debug startGame response ${response}`)
      if (response.status === 'success')
      {
        alert("La partie va commencer !");
      }
      else
      {
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

              case 'border_collision':
                  // Wave effect
                  ctx.strokeStyle = 'white';
                  ctx.lineWidth = 3 * (1 - progress);
                  const waveWidth = 60;
                  const waveAmplitude = 10 * (1 - progress);
                  
                  ctx.beginPath();
                  for (let i = -waveWidth/2; i <= waveWidth/2; i++) {
                      const x = effect.x + i;
                      const y = effect.y + Math.sin(i * 0.1 + progress * 10) * waveAmplitude;
                      if (i === -waveWidth/2) ctx.moveTo(x, y);
                      else ctx.lineTo(x, y);
                  }
                  ctx.stroke();
                  break;
                  
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

    function handleResize() {
      const container = document.querySelector('.game-container');
      if (!container) return;
  
      const containerWidth = container.clientWidth;
      const containerHeight = container.clientHeight;
      
      // Calculate new scale
      scale = Math.min(containerWidth / ORIGINAL_WIDTH, containerHeight / ORIGINAL_HEIGHT);
      
      // Set canvas style size
      canvas.style.width = (ORIGINAL_WIDTH * scale) + 'px';
      canvas.style.height = (ORIGINAL_HEIGHT * scale) + 'px';
      
      // Keep canvas resolution sharp
      canvas.width = ORIGINAL_WIDTH;
      canvas.height = ORIGINAL_HEIGHT;
      
      // Reset context properties
      ctx.imageSmoothingEnabled = false;
    }
  
    window.addEventListener('resize', handleResize);
    handleResize(); // Initial
  
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
  
    // -- Gestion PowerUp SVG / Bumper SVG (extraits de ton code)
    function createPowerupSVG(type) {
      const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.setAttribute("viewBox", "0 0 50 50");
      svg.setAttribute("width", "30");
      svg.setAttribute("height", "30");
      
      const powerupStyles = {
          'invert': {
              colors: {main: '#FF69B4', glow: '#FF1493'},
              icon: 'M25 15 A10 10 0 1 1 25 35 M25 35 L20 30 M25 35 L30 30'
          },
          'shrink': {
              colors: {main: '#FF0000', glow: '#8B0000'},
              icon: 'M25 25 L35 15 M33 15 L35 15 L35 17 M25 25 L15 15 M17 15 L15 15 L15 17 M25 25 L35 35 M33 35 L35 35 L35 33 M25 25 L15 35 M17 35 L15 35 L15 33'
          },
          'ice': {
              colors: {main: '#00FFFF', glow: '#00CED1'},
              paths: [
                  {d: 'M25 10 L25 40 M18 14 L32 36 M32 14 L18 36 M20 25 L30 25', 
                  fill: 'none', stroke: 'white', width: 3},
                  {d: 'M25 25 m-3,0 a3,3 0 1,0 6,0 a3,3 0 1,0 -6,0', 
                  fill: 'white', stroke: 'none', width: 0}
              ]
          },
          'speed': {
              colors: {main: '#FFD700', glow: '#FFA500'},
              icon: 'M30 10 L20 25 L27 25 L17 40 L32 25 L25 25 L35 10',
              fill: 'white'
          },
          'flash': {
              colors: {main: '#FFFF00', glow: '#FFD700'},
              paths: [
                  {d: 'M25 10 m-8,0 a8,8 0 1,0 16,0 a8,8 0 1,0 -16,0', 
                  fill: 'white', stroke: 'none', width: 0},
                  {d: 'M25 10 L25 17 M25 33 L25 40 M35 25 L42 25 M8 25 L15 25 M32 18 L37 13 M13 37 L18 32 M32 32 L37 37 M13 13 L18 18',
                  fill: 'none', stroke: 'white', width: 3}
              ]
          },
          'sticky': {
              colors: {main: '#32CD32', glow: '#228B22'},
              icon: 'M25 10 C15 10 15 20 25 20 C35 20 35 10 25 10 M17 20 C17 40 33 40 33 20',
              fill: 'white'
          }
      };
      
      const style = powerupStyles[type] || powerupStyles['speed'];
      
      // Create gradient
      const gradient = document.createElementNS("http://www.w3.org/2000/svg", "radialGradient");
      gradient.id = `${type}Glow`;
      
      const stops = [
          {offset: '0%', color: style.colors.main, opacity: '1'},
          {offset: '100%', color: style.colors.glow, opacity: '0.6'}
      ];
      
      stops.forEach(stop => {
          const stopEl = document.createElementNS("http://www.w3.org/2000/svg", "stop");
          stopEl.setAttribute("offset", stop.offset);
          stopEl.setAttribute("stop-color", stop.color);
          stopEl.setAttribute("stop-opacity", stop.opacity);
          gradient.appendChild(stopEl);
      });
      
      svg.appendChild(gradient);
      
      // Create base circle
      const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      circle.setAttribute("cx", "25");
      circle.setAttribute("cy", "25");
      circle.setAttribute("r", "20");
      circle.setAttribute("fill", `url(#${type}Glow)`);
      svg.appendChild(circle);
      
      // Add icon(s)
      if (style.paths) {
          // For complex icons with multiple paths
          style.paths.forEach(pathData => {
              const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
              path.setAttribute("d", pathData.d);
              path.setAttribute("stroke", pathData.stroke);
              path.setAttribute("stroke-width", pathData.width);
              path.setAttribute("fill", pathData.fill);
              svg.appendChild(path);
          });
      } else {
          // For single path icons
          const icon = document.createElementNS("http://www.w3.org/2000/svg", "path");
          icon.setAttribute("d", style.icon);
          icon.setAttribute("stroke", "white");
          icon.setAttribute("stroke-width", "3");
          icon.setAttribute("fill", style.fill || "none");
          svg.appendChild(icon);
      }
      
      return `data:image/svg+xml;base64,${btoa(new XMLSerializer().serializeToString(svg))}`;
    }
  
    function createBumperSVG() {
      const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.setAttribute("viewBox", "0 0 100 100");
      
      // Create white orb gradient
      const whiteGradient = document.createElementNS("http://www.w3.org/2000/svg", "radialGradient");
      whiteGradient.id = "whiteOrbGradient";
      whiteGradient.setAttribute("cx", "40%");
      whiteGradient.setAttribute("cy", "40%");
      whiteGradient.setAttribute("r", "60%");
      
      const whiteStops = [
        {offset: '0%', color: 'white', opacity: '1'},
        {offset: '90%', color: '#e0e0e0', opacity: '1'}
      ];
      
      whiteStops.forEach(stop => {
        const stopEl = document.createElementNS("http://www.w3.org/2000/svg", "stop");
        stopEl.setAttribute("offset", stop.offset);
        stopEl.setAttribute("stop-color", stop.color);
        stopEl.setAttribute("stop-opacity", stop.opacity);
        whiteGradient.appendChild(stopEl);
      });
      
      // Create blue ring gradient
      const blueGradient = document.createElementNS("http://www.w3.org/2000/svg", "radialGradient");
      blueGradient.id = "blueRingGradient";
      blueGradient.setAttribute("cx", "50%");
      blueGradient.setAttribute("cy", "50%");
      blueGradient.setAttribute("r", "50%");
      
      const blueStops = [
        {offset: '0%', color: '#4169E1', opacity: '1'},
        {offset: '100%', color: '#1E90FF', opacity: '1'}
      ];
      
      blueStops.forEach(stop => {
        const stopEl = document.createElementNS("http://www.w3.org/2000/svg", "stop");
        stopEl.setAttribute("offset", stop.offset);
        stopEl.setAttribute("stop-color", stop.color);
        stopEl.setAttribute("stop-opacity", stop.opacity);
        blueGradient.appendChild(stopEl);
      });
      
      // Add gradients to defs
      const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
      defs.appendChild(whiteGradient);
      defs.appendChild(blueGradient);
      svg.appendChild(defs);
      
      // Blue exterior ring
      const ringCircle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      ringCircle.setAttribute("cx", "50");
      ringCircle.setAttribute("cy", "50");
      ringCircle.setAttribute("r", "45");
      ringCircle.setAttribute("fill", "none");
      ringCircle.setAttribute("stroke", "url(#blueRingGradient)");
      ringCircle.setAttribute("stroke-width", "8");
      
      // White orb center
      const whiteOrb = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      whiteOrb.setAttribute("cx", "50");
      whiteOrb.setAttribute("cy", "50");
      whiteOrb.setAttribute("r", "35");
      whiteOrb.setAttribute("fill", "url(#whiteOrbGradient)");
      
      // Highlight for 3D effect
      const highlight = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      highlight.setAttribute("cx", "35");
      highlight.setAttribute("cy", "35");
      highlight.setAttribute("r", "15");
      highlight.setAttribute("fill", "white");
      highlight.setAttribute("opacity", "0.3");
      
      svg.appendChild(ringCircle);
      svg.appendChild(whiteOrb);
      svg.appendChild(highlight);
      
      return `data:image/svg+xml;base64,${btoa(new XMLSerializer().serializeToString(svg))}`;
    }
    const powerupImages = {
      'invert': new Image(),
      'shrink': new Image(),
      'ice': new Image(),
      'speed': new Image(),
      'flash': new Image(),
      'sticky': new Image()
    };
  
    function initPowerupImages() {
      Object.keys(powerupImages).forEach(type => {
        powerupImages[type].src = createPowerupSVG(type);
      });
    }
    initPowerupImages();
  
    const bumperImage = new Image();
    bumperImage.src = createBumperSVG();
  
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
        ctx.fillStyle = 'black';
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
        gameState.powerups.forEach(orb => {
          const type = orb.type || 'speed';
          const img = powerupImages[type];
          if (img.complete) {
            ctx.save();
            
            const glowColors = {
              'invert': '#FF69B4',
              'shrink': '#FF0000',
              'ice': '#00FFFF',
              'speed': '#FFD700',
              'flash': '#FFFF00',
              'sticky': '#32CD32'
            };
            
            ctx.shadowColor = glowColors[type] || glowColors['speed'];
            ctx.shadowBlur = 10 * scale;
            
            ctx.drawImage(img,
              orb.x - 15,
              orb.y - 15,
              30,
              30
            );
            
            ctx.restore();
          }
        });
  
        // Bumpers
        gameState.bumpers.forEach(bumper => {
          if (bumperImage.complete) {
            ctx.save();
            ctx.shadowColor = '#4169E1';
            ctx.shadowBlur = 10 * scale;
            ctx.drawImage(bumperImage,
              bumper.x - bumper.size,
              bumper.y - bumper.size,
              bumper.size * 2,
              bumper.size * 2
            );
            ctx.restore();
          }
        });
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
      requestAnimationFrame(draw);
    }
  
    // Lancer la boucle de rendu
    requestAnimationFrame(draw);
  }
  