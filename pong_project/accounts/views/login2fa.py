# ---- Imports standard ----
import base64
from io import BytesIO
import logging

# ---- Imports tiers ----
import pyotp
import qrcode

from django.http import JsonResponse
from django.views import View
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model

from django.contrib.auth import login
from django.shortcuts import get_object_or_404
from accounts.utils import generate_jwt_token

from accounts.forms import TwoFactorLoginForm

# ---- Configuration ----
logger = logging.getLogger(__name__)
User = get_user_model()


class Base2FAView(View):
    """
    Base class for 2FA views, providing common utilities.
    """

    def generate_totp_qr(self, user, secret):
        """
        Generate a QR code for TOTP setup.
        """
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(name=user.username, issuer_name="Transcendence")
        
        img = qrcode.make(provisioning_uri)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_code = base64.b64encode(buffered.getvalue()).decode()
        
        return qr_code
# [IMPROVE] le code secret ne doit pas être envoyé au client
@method_decorator(login_required, name='dispatch')
class Enable2FAView(Base2FAView):
    """
    Enable 2FA for the authenticated user.
    """

    def get(self, request):
        if request.user.is_2fa_enabled:
            return JsonResponse({'status': 'error', 'message': '2FA is already enabled on your account.'}, status=400)

        # Génération du secret et du QR code
        secret = pyotp.random_base32()
        qr_code = self.generate_totp_qr(request.user, secret)

        # Stockage du secret dans la session (expire en 5 minutes)
        request.session['totp_secret'] = secret
        request.session.set_expiry(300)

        # Générer le HTML pour le formulaire
        html_content = render_to_string('accounts/enable_2fa.html', {
            'qr_code': qr_code,
            '2FA_form': TwoFactorLoginForm()  # Méthode qui retourne le formulaire
        })

        # Renvoyer le JSON avec le HTML inclus
        return JsonResponse({
            'status': 'success',
            'html': html_content
        })

@method_decorator(login_required, name='dispatch')
class Check2FAView(View):
    """
    Verify the TOTP code to enable 2FA.
    """

    def post(self, request):
        totp_secret = request.session.get('totp_secret')
        if not totp_secret:
            return JsonResponse({'status': 'error', 'message': 'No 2FA setup in progress.'}, status=400)

        code = request.POST.get('code')
        if not code:
            return JsonResponse({'status': 'error', 'message': 'Code is required.'}, status=400)

        totp = pyotp.TOTP(totp_secret)
        if totp.verify(code):
            request.user.totp_secret = totp_secret
            request.user.is_2fa_enabled = True
            request.user.save()
            del request.session['totp_secret']
            return JsonResponse({'status': 'success', 'message': '2FA has been successfully enabled.'})

        return JsonResponse({'status': 'error', 'message': 'Invalid 2FA code.'}, status=400)




class Login2faView(View):
    """
    Verify 2FA code during login.
    """

    def get(self, request):
        """
        Gère une requête HTTP GET.
        Retourne un formulaire de connexion sous forme de HTML encapsulé dans une réponse JSON.
        """
      
        # Créez une instance de TwoFactorLoginForm
        login2fa_form = TwoFactorLoginForm()

         # Générer le HTML pour le formulaire
          # Générer le HTML pour le formulaire avec RequestContext
        html_content = render_to_string(
            'accounts/login2fa.html',
            {'login2fa_form': login2fa_form},
            request=request  # Inclut le RequestContext pour le token CSRF
        )
        return JsonResponse({
            'status': 'success',
            'html': html_content,  # Renommé pour être plus explicite
        })

    def post(self, request):
        user_id = request.session.get('user_id')
        auth_partial = request.session.get('auth_partial')

        if not user_id or not auth_partial:
            return JsonResponse({'status': 'error', 'message': 'Unauthorized access.'}, status=403)

        user = get_object_or_404(User, id=user_id)
        code = request.POST.get('code')

        if not code:
            return JsonResponse({'status': 'error', 'message': 'Code is required.'}, status=400)

        logger.debug(f"Received 2FA code: {code}")

        totp = pyotp.TOTP(user.totp_secret)
        if totp.verify(code):

            token_jwt = generate_jwt_token(user)
            user.is_online = True
            user.save()
            login(request, user)
            del request.session['auth_partial']

            logger.debug(f"Utilisateur connecté après login: {request.user.is_authenticated}")

            return JsonResponse({
                'status': 'success',
                'access_token': token_jwt['access_token'],
                'refresh_token': token_jwt['refresh_token'],
                'ís_authenticated': True,
                'message': '2FA verified successfully. Login successful.'
            })
        return JsonResponse({'status': 'error', 'message': 'Invalid 2FA code.'}, status=400)


@method_decorator(login_required, name='dispatch')
class Disable2FAView(View):
    """
    Disable 2FA for the authenticated user.
    """

    def get(self, request):
        if not request.user.is_2fa_enabled:
            return JsonResponse({'status': 'error', 'message': '2FA is not enabled on your account.'}, status=400)

        # Créez une instance de TwoFactorLoginForm
        disable_form = TwoFactorLoginForm()

         # Générer le HTML pour le formulaire
        html_content = render_to_string('accounts/disable_2fa.html', {
            'disable_form': disable_form,
        })
        return JsonResponse({
            'status': 'success',
            'html': html_content
        })

    def post(self, request):
        if not request.user.is_2fa_enabled:
            return JsonResponse({'status': 'error', 'message': '2FA is not enabled on your account.'}, status=400)

        code = request.POST.get('code')
        if not code:
            return JsonResponse({'status': 'error', 'message': 'Code is required.'}, status=400)

        totp = pyotp.TOTP(request.user.totp_secret)
        if totp.verify(code):
            request.user.totp_secret = ''
            request.user.is_2fa_enabled = False
            request.user.save()
            return JsonResponse({'status': 'success', 'message': '2FA has been disabled.'})

        return JsonResponse({'status': 'error', 'message': 'Invalid 2FA code.'}, status=400)
