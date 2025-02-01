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


export async function launchLiveGameWithOptions(gameId, userRole, urlStartButton) {
  const protocol = (window.location.protocol === 'https:') ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws/pong/${gameId}/`;

  let startGameSelector = null;
  let onStartGame = null;

  if (urlStartButton) {
    startGameSelector = "#startGameBtn";
    // fonction qui lance le jeu après appui sur #startGameBtn
    onStartGame = async (gameId) => {
      const url = urlStartButton;
      const formData = new FormData();
      formData.append('game_id', gameId);

      const response = await requestPost('game', url, formData);
      if (response.status === 'success') {
        alert("La partie va commencer !");
      } else {
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
    const startGameBtn = document.querySelector(config.startGameSelector || "#startGameBtn");
  
    // 2) Gérer le bouton "Start" (optionnel)
    if (startGameBtn && config.onStartGame) {
      // Débloquer le bouton après 3s (optionnel)
      setTimeout(() => { startGameBtn.disabled = false; }, 3000);
  
      // Clic => on appelle la callback onStartGame
      startGameBtn.addEventListener('click', async () => {
        await config.onStartGame(config.gameId);
      });
    }
  
    // 3) Mise en place du redimensionnement du canvas
    const ORIGINAL_WIDTH = 800;
    const ORIGINAL_HEIGHT = 400;
    let scale = 1;
  
    function handleResize() {
      const container = document.querySelector('.game-container');
      if (!container) return;
  
      const containerWidth = container.clientWidth;
      const containerHeight = container.clientHeight;
  
      scale = Math.min(containerWidth / ORIGINAL_WIDTH, containerHeight / ORIGINAL_HEIGHT);
  
      canvas.style.width = (ORIGINAL_WIDTH * scale) + 'px';
      canvas.style.height = (ORIGINAL_HEIGHT * scale) + 'px';
  
      canvas.width = ORIGINAL_WIDTH;
      canvas.height = ORIGINAL_HEIGHT;
  
      ctx.imageSmoothingEnabled = false;
    }
    window.addEventListener('resize', handleResize);
    handleResize(); // initial
  
    // 4) Initialiser WebSocket
    const socket = new WebSocket(config.wsUrl);
    
    socket.onopen = () => {
      console.log("[live_game_utils] WebSocket connection opened:", config.wsUrl);
    };
    socket.onclose = () => {
      console.log("[live_game_utils] WebSocket connection closed.");
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
      }
      else if (data.type === 'game_over') {
        console.log("[live_game_utils] Game over detected");
        alert("Game Over! Winner = " + data.winner);
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
        socket.send(JSON.stringify({ action, player, direction }));
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
        socket.send(JSON.stringify({ action, player }));
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
  
    // 9) La boucle de dessin
    function draw() {
      if (gameState.flash_effect) {
        ctx.fillStyle = 'white';
        ctx.fillRect(0,0,canvas.width, canvas.height);
      } else {
        ctx.fillStyle = 'black';
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
      ctx.fillStyle = 'white';
      ctx.font = '20px Arial';
      ctx.fillText(""+ gameState.score_left, 20, 30);
      ctx.fillText(""+ gameState.score_right, canvas.width-40, 30);
  
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
  