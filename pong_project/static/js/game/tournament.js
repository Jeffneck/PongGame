"use strict";
import { requestGet, requestPost } from "../api/index.js";
import { showStatusMessage, updateHtmlContent } from "../tools/index.js";
import { launchLiveGameWithOptions } from "./live_game.js";
import { TournamentNextMatch } from "./tournament_utils.js";
import { showResults } from "./gameResults.js";
import { navigateTo } from "../router.js";

export async function handleTournament() {
  if (!localStorage.getItem('access_token')) {
    navigateTo('/');
    return;
  }
  let tournamentParam = sessionStorage.getItem('params');
  if (!tournamentParam) {
    showStatusMessage("Paramètres de tournoi invalides.", 'error');
    navigateTo('/game-options');
    return;
  }
  try {
    tournamentParam = JSON.parse(tournamentParam);
  } catch (e) {
    showStatusMessage("Erreur lors de la récupération des paramètres.", 'error');
    return;
  }
  const formHtml = await getTournamentForm();
  if (!formHtml) return;
  updateHtmlContent('#content', formHtml);
  const form = document.querySelector('#content form');
  if (!form) {
    console.error("Formulaire introuvable.");
    return;
  }
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    if (tournamentParam) {
      formData.set('ball_speed', tournamentParam.ball_speed);
      formData.set('paddle_size', tournamentParam.paddle_size);
      formData.set('bonus_enabled', tournamentParam.bonus_enabled);
      formData.set('obstacles_enabled', tournamentParam.obstacles_enabled);
    }
    try {
      const response = await createTournament(formData);
      if (response.status === 'success') {
        alert(`Tournoi créé : ID = ${response.tournament_id}`);
        await runTournamentFlow(response.tournament_id);
      } else {
        alert("Erreur : " + response.message);
      }
    } catch (error) {
      console.error("Erreur lors de la création du tournoi :", error);
      alert("Erreur lors de la création du tournoi.");
    }
  });
}

async function getTournamentForm() {
  const responseGet = await requestGet('game', 'create_tournament');
  if (!responseGet) return false;
  if (responseGet.status === 'success') {
    return responseGet.html;
  } else {
    showStatusMessage("Erreur lors de la récupération du formulaire du tournoi.", 'error');
    navigateTo('/game-options');
  }
}

async function createTournament(formData) {
  return await requestPost('game', 'create_tournament', formData);
}

async function runTournamentFlow(tournamentId) {
  while (true) {
    const bracketResp = await requestGet('game', `tournament_bracket/${tournamentId}`);
    if (!bracketResp || bracketResp.status !== "success") {
      console.error("Erreur de récupération du bracket.");
      break;
    }
    updateHtmlContent("#content", bracketResp.html);
    updateBracketUI(bracketResp);
    await delay(3000);
    if (bracketResp.tournament_status === "finished") {
      console.log("Tournoi terminé.");
      break;
    }
    const nextResp = await requestGet('game', `tournament_next_game/${tournamentId}`);
    if (!nextResp || nextResp.status !== "success") {
      console.error("Erreur de récupération du prochain match.");
      break;
    }
    if (nextResp.next_match_type === "finished") {
      console.log("Tournoi terminé (next game).");
      break;
    }
    updateHtmlContent("#content", nextResp.html);
    updateNextGameUI(bracketResp, nextResp);
    TournamentNextMatch();
    await delay(3000);
    const gameId = await createTournamentGameSession(tournamentId, nextResp.next_match_type);
    if (!gameId) {
      console.error("Erreur lors de la création de la session de match.");
      break;
    }
    await launchLiveGameWithOptions(gameId, 'both', `start_tournament_game_session/${gameId}`);
	// on vérifie le status côté serveur avant de continuer la loop
	const statusResponse = await requestGet('game', `get_game_status/${gameId}`);
	if (statusResponse.status === 'success' && statusResponse.session_status === 'cancelled') {
		showStatusMessage('Un des joueurs s\'est deconnecte, tournoi annule ...', 'error');
		break
	}
  }
  sessionStorage.removeItem('tournamentparams');
  console.log("Fin du flux tournoi.");
}

function updateNextGameUI(bracketResp, nextResp) {
  const matchType = nextResp.next_match_type;
  let leftPlayerName = "";
  let rightPlayerName = "";
  let leftPlayerAvatar = "";
  let rightPlayerAvatar = "";
  const avatars = bracketResp.player_avatars;
  switch (matchType) {
    case "semifinal1":
      leftPlayerName = bracketResp.player1;
      rightPlayerName = bracketResp.player2;
      leftPlayerAvatar = avatars[bracketResp.player1];
      rightPlayerAvatar = avatars[bracketResp.player2];
      break;
    case "semifinal2":
      leftPlayerName = bracketResp.player3;
      rightPlayerName = bracketResp.player4;
      leftPlayerAvatar = avatars[bracketResp.player3];
      rightPlayerAvatar = avatars[bracketResp.player4];
      break;
    case "final":
      leftPlayerName = bracketResp.winner_semifinal_1;
      rightPlayerName = bracketResp.winner_semifinal_2;
      leftPlayerAvatar = avatars[bracketResp.winner_semifinal_1] || "/static/svg/default_avatar.svg";
      rightPlayerAvatar = avatars[bracketResp.winner_semifinal_2] || "/static/svg/default_avatar.svg";
      break;
    default:
      console.error("Type de match inconnu :", matchType);
      return;
  }
  const leftAvatarImg = document.querySelector(".avatar1 img.avatar");
  const leftNameElem = document.querySelector(".avatar1 .player-name");
  const rightAvatarImg = document.querySelector(".avatar2 img.avatar");
  const rightNameElem = document.querySelector(".avatar2 .player-name");
  if (leftAvatarImg) leftAvatarImg.src = leftPlayerAvatar;
  if (leftNameElem) leftNameElem.textContent = leftPlayerName;
  if (rightAvatarImg) rightAvatarImg.src = rightPlayerAvatar;
  if (rightNameElem) rightNameElem.textContent = rightPlayerName;
  console.debug("Next match type:", matchType);
}

async function createTournamentGameSession(tournamentId, nextMatchType) {
  try {
    const formData = new FormData();
    formData.set('next_match_type', nextMatchType);
    const response = await requestPost('game', `create_tournament_game_session/${tournamentId}`, formData);
    if (response.status === 'success') {
      updateHtmlContent("#content", response.html);
      return response.game_id;
    } else {
      console.error("Erreur createTournamentGameSession:", response.message);
      return null;
    }
  } catch (err) {
    console.error("Exception createTournamentGameSession:", err);
    return null;
  }
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}


