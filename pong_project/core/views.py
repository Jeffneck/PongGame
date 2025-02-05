from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
import logging
import json
from pong_project.decorators import user_not_authenticated
from accounts.views.burgerMenu import get_burger_menu_context




logger = logging.getLogger(__name__)



def not_found_view(request):
    """
    Retourne la page 404 sous forme de JSON avec son contenu HTML.
    """
    logger.debug("Entre dans not_found_view")
    not_found_html = render_to_string('core/404.html')  # Assurez-vous que le template se trouve dans le bon dossier
    return JsonResponse({
        'status': 'success',
        'html': not_found_html
    })


def get_navbar(request):
    """
    Génère et retourne le contenu de la barre de navigation sous forme de JSON.
    """
    logger.debug("Entre dans get_navbar_view")
    is_authenticated = request.user.is_authenticated

    logger.debug("is_authenticated : " + str(is_authenticated))

    if is_authenticated:
        # Utilise le contexte du burger menu pour obtenir les données
        burger_menu_context = get_burger_menu_context(request.user)
        burger_menu_html = render_to_string('accounts/burger_menu.html', burger_menu_context)

        # Inclure avatar_url explicitement dans le contexte
        navbar_html = render_to_string('core/navbar_logged_in.html', {
            'burger_menu': burger_menu_html,
            'avatar_url': burger_menu_context['avatar_url'],  # Passer l'URL de l'avatar
        })
        logger.debug("Navbar générée pour un utilisateur connecté")
    else:
        # Génération de la navbar publique
        navbar_html = render_to_string('core/navbar_public.html')
        logger.debug("Navbar générée pour un utilisateur non connecté")

    return JsonResponse({
        'status': 'success',
        'is_authenticated': is_authenticated,
        'html': navbar_html
    })

@user_not_authenticated
def home_view(request):
    """
    Retourne la page d'accueil sous forme de JSON avec son contenu HTML.
    """
    logger.debug("Entre dans home_view")
    home_html = render_to_string('core/home.html')
    return JsonResponse({
        'status': 'success',
        'html': home_html
    })


def landing_view(request):
    """
    Retourne la page de destination avec un état d'authentification dans une réponse JSON.
    """
    logger.debug("Entre dans landing_view")
    # IMPROVE html au lieu de json
    return render(request, 'core/landing.html')