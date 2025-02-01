import { requestGet, requestPost } from "../api/index.js";
import { updateHtmlContent } from "../tools/index.js";
import { launchLiveGameWithOptions } from './live_game.js';

// Fonction principale appelée quand on clique sur "Lancer Tournoi" dans le menu
export async function handleTournament(tournamentParam) {
  // 1) Récupère le formulaire (GET)
  const formHtml = await getTournamentForm();
  updateHtmlContent('#content', formHtml);

  // 2) Sélection du form dans le DOM
  const form = document.querySelector('#content form');
  if (!form) {
    console.error("Formulaire introuvable dans le HTML injecté.");
    return;
  }

  // 3) Au submit => POST de création du tournoi
  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    // Récupération des champs du form
    const formData = new FormData(form);

    // Si vous avez d’autres paramètres passés depuis un menu (tournamentParam),
    // on peut forcer/écraser ici dans le formData :
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
        // Lance la suite (loop + affichage bracket + next match etc.)
        await runTournamentFlow(response.tournament_id);
      } else {
        alert("Erreur : " + response.message);
      }
    } catch (error) {
      console.error("Erreur lors de la création du tournoi :", error);
      alert("Une erreur est survenue lors de la création du tournoi.");
    }
  });
}

// -- Petites fonctions factorielles pour clarifier --

async function getTournamentForm() {
  const responseGet = await requestGet('game', 'create_tournament');
  if (responseGet.status === 'success') {
    return responseGet.html;
  } else {
    console.error("Impossible de récupérer le formulaire du tournoi");
    return "<p>Erreur chargement formulaire</p>";
  }
}

async function createTournament(formData) {
  // Appel POST vers /game/create_tournament
  return await requestPost('game', 'create_tournament', formData);
}

// -- Le “flow” du tournoi (récup bracket, next match, etc.) --

async function runTournamentFlow(tournamentId) {
  while (true) {
    // 1) Afficher le bracket
    const bracketResp = await requestGet('game', `tournament_bracket/${tournamentId}`);
    if (!bracketResp || bracketResp.status !== "success") {
      console.error("Impossible de récupérer le bracket du tournoi.");
      break;
    }

    
    updateHtmlContent("#content", bracketResp.html);
    updateBracketUI(bracketResp)
    await delay(4000);  // Pause de 4s (si vraiment nécessaire)
    
    // TODO : si le backend renvoie un champ indiquant “finished”, sortir de la boucle
    // Exemple si bracketResp renvoie un `tournament_finished: true` ou
    // un champ `tournament_status = "finished"`.
    if (bracketResp.tournament_status === "finished") {
      console.log("Tournoi terminé (d’après bracket).");
      break;
    }
    // 2) Récupérer les joueurs du prochain match
    const nextResp = await requestGet('game', `tournament_next_game/${tournamentId}`);
    if (!nextResp || nextResp.status !== "success") {
      console.error("Impossible de récupérer le prochain match.");
      break;
    }

    if (nextResp.next_match_type === "finished") {
      console.log("Tournoi terminé (d’après next_game).");
      break;
    }

    updateHtmlContent("#content", nextResp.html);
    await delay(3000);

    // 3) Créer la gameSession de match (semi1, semi2, finale…) en POST
    const gameId = await createTournamentGameSession(tournamentId, nextResp.next_match_type);
    if (!gameId) {
      console.error("Erreur lors de la création de la session de match.");
      break;
    }

    // 4) Lancer le liveGame 
    await launchLiveGameWithOptions(gameId, 'both', `start_tournament_game_session/${gameId}`);
  }

  console.log("Fin du flux tournoi");
}



// Met à jour le bracket en fonction de l'état du tournoi
// Improve remplacer par des balises django dans le front ??
function updateBracketUI(bracketResp) {
  const status = bracketResp.tournament_status;
  const winnerSemi1 = bracketResp.winner_semifinal_1;
  const winnerSemi2 = bracketResp.winner_semifinal_2;
  const winnerFinal = bracketResp.winner_final;

  document.querySelectorAll('.tournament-title p').forEach(p => p.classList.add('d-none'));

  if (status === "semifinal1_in_progress") {
    document.querySelector('.tournament-title p:nth-child(2)').classList.remove('d-none'); 
    document.querySelector('.eclair.match-1').classList.remove('d-none');
  } else if (status === "semifinal2_in_progress") {
    document.querySelector('.tournament-title p:nth-child(3)').classList.remove('d-none');
    document.querySelector('.eclair.match-2').classList.remove('d-none');
  } else if (status === "final_in_progress") {
    document.querySelector('.tournament-title p:nth-child(4)').classList.remove('d-none');
    document.querySelector('.eclair.match-3').classList.remove('d-none');
  } else if (status === "finished") {
    document.querySelector('.tournament-title p:nth-child(5)').classList.remove('d-none');
  }

  if (winnerSemi1) {
    document.querySelector(".winner1").classList.remove("d-none");
    document.querySelector(".winner1 .avatar").src = `svg/${winnerSemi1}.svg`;
    document.querySelector(".winner1 .player-name").textContent = winnerSemi1;
  }

  if (winnerSemi2) {
    document.querySelector(".winner2").classList.remove("d-none");
    document.querySelector(".winner2 .avatar").src = `svg/${winnerSemi2}.svg`;
    document.querySelector(".winner2 .player-name").textContent = winnerSemi2;
  }

  if (winnerFinal) {
    document.querySelector(".winner3").classList.remove("d-none");
    document.querySelector(".winner3 .avatar").src = `svg/${winnerFinal}.svg`;
    document.querySelector(".winner3 .winner-name").textContent = winnerFinal;
  }
}

// Création de la session (POST vers /game/create_tournament_game_session/<tournament_id>)
async function createTournamentGameSession(tournamentId, nextMatchType) {
  try {
    const formData = new FormData();
    formData.set('next_match_type', nextMatchType);

    const response = await requestPost(
      'game',
      `create_tournament_game_session/${tournamentId}`,
      formData
    );
    if (response.status === 'success') {
      updateHtmlContent("#content", response.html);
      return response.game_id; // On retourne juste l’ID
    } else {
      console.error("createTournamentGameSession error:", response.message);
      return null;
    }
  } catch (err) {
    console.error("createTournamentGameSession exception:", err);
    return null;
  }
}


// Petit utilitaire de pause asynchrone
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
