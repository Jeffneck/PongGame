import base64
from io import BytesIO
import logging

import pyotp
import qrcode

from django.http import JsonResponse
from django.views import View
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model, login
from django.shortcuts import get_object_or_404

from accounts.utils import generate_jwt_token
from pong_project.decorators import login_required_json, auth_partial_required
from accounts.forms import TwoFactorLoginForm
from pong_project.decorators import user_not_authenticated

from django.utils.translation import gettext as _  # Import pour la traduction

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
        try:
            totp = pyotp.TOTP(secret)
            # Create the provisioning URI with the issuer name.
            provisioning_uri = totp.provisioning_uri(name=user.username, issuer_name="Transcendence")
            img = qrcode.make(provisioning_uri)
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            qr_code = base64.b64encode(buffered.getvalue()).decode()
            return qr_code
        except Exception as e:
            logger.exception("Error generating QR code: %s", e)
            raise


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class Enable2FAView(Base2FAView):
    """
    Enable 2FA for the authenticated user.
    """
    def get(self, request):
        if request.user.is_2fa_enabled:
            return JsonResponse({
                'status': 'error',
                'message': _("2FA is already enabled on your account.")
            }, status=400)
        try:
            # Generate a new secret and corresponding QR code
            secret = pyotp.random_base32()
            qr_code = self.generate_totp_qr(request.user, secret)
    
            # Store the secret in the session (expires in 5 minutes)
            request.session['totp_secret'] = secret
            request.session.set_expiry(300)
    
            # Render the 2FA enablement form without exposing the secret in clear text
            html_content = render_to_string('accounts/enable_2fa.html', {
                'qr_code': qr_code,
                '2FA_form': TwoFactorLoginForm(),
            })
    
            return JsonResponse({
                'status': 'success',
                'html': html_content,
            }, status=200)
        except Exception as e:
            logger.exception("Error in Enable2FAView GET: %s", e)
            return JsonResponse({
                'status': 'error',
                'message': _("An error occurred while enabling 2FA.")
            }, status=500)


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
@method_decorator(require_POST, name='dispatch')
class Check2FAView(View):
    """
    Verify the TOTP code to enable 2FA.
    """
    def post(self, request):
        try:
            totp_secret = request.session.get('totp_secret')
            if not totp_secret:
                return JsonResponse({
                    'status': 'error',
                    'message': _("No 2FA setup in progress.")
                }, status=400)
    
            code = request.POST.get('code')
            if not code:
                return JsonResponse({
                    'status': 'error',
                    'message': _("Code is required.")
                }, status=400)
    
            totp = pyotp.TOTP(totp_secret)
            if totp.verify(code):
                request.user.totp_secret = totp_secret
                request.user.is_2fa_enabled = True
                request.user.save()
                # Remove the secret from the session after successful verification
                if 'totp_secret' in request.session:
                    del request.session['totp_secret']
                return JsonResponse({
                    'status': 'success',
                    'message': _("2FA has been successfully enabled.")
                }, status=200)
    
            return JsonResponse({
                'status': 'error',
                'message': _("Invalid 2FA code.")
            }, status=400)
        except Exception as e:
            logger.exception("Unexpected error in Check2FAView: %s", e)
            return JsonResponse({
                'status': 'error',
                'message': _("An unexpected error occurred.")
            }, status=500)


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(user_not_authenticated, name='dispatch')
@method_decorator(auth_partial_required, name='dispatch')
class Login2faView(View):
    """
    Verify 2FA code during login.
    """
    def get(self, request):
        """
        Return the 2FA login form as HTML embedded in JSON.
        """
        try:
            login2fa_form = TwoFactorLoginForm()
            html_content = render_to_string(
                'accounts/login2fa.html',
                {'login2fa_form': login2fa_form},
                request=request  # To include RequestContext for CSRF token
            )
            return JsonResponse({
                'status': 'success',
                'html': html_content,
            }, status=200)
        except Exception as e:
            logger.exception("Error rendering 2FA login form: %s", e)
            return JsonResponse({
                'status': 'error',
                'message': _("An error occurred while rendering the form.")
            }, status=500)
    
    @method_decorator(require_POST, name='dispatch')
    def post(self, request):
        try:
            logger.debug("user id: %s", request.session.get('user_id'))
            logger.debug("auth_partial: %s", request.session.get('auth_partial'))
            user_id = request.session.get('user_id')
            auth_partial = request.session.get('auth_partial')
    
            if not user_id or not auth_partial:
                return JsonResponse({
                    'status': 'error',
                    'message': _("Unauthorized access.")
                }, status=403)
    
            user = get_object_or_404(User, id=user_id)
            code = request.POST.get('code')
            if not code:
                return JsonResponse({
                    'status': 'error',
                    'message': _("Code is required.")
                }, status=400)
    
            logger.debug("Received 2FA code submission.")
    
            totp = pyotp.TOTP(user.totp_secret)
            if totp.verify(code):
                token_jwt = generate_jwt_token(user)
                user.is_online = True
                user.save()
                login(request, user)
                if 'auth_partial' in request.session:
                    del request.session['auth_partial']
    
                logger.debug("User authenticated successfully: %s", user.username)
                return JsonResponse({
                    'status': 'success',
                    'access_token': token_jwt['access_token'],
                    'refresh_token': token_jwt['refresh_token'],
                    'is_authenticated': True,
                    'message': _("2FA verified successfully. Login successful.")
                }, status=200)
    
            return JsonResponse({
                'status': 'error',
                'message': _("Invalid 2FA code.")
            }, status=400)
        except Exception as e:
            logger.exception("Unexpected error in Login2faView POST: %s", e)
            return JsonResponse({
                'status': 'error',
                'message': _("An unexpected error occurred.")
            }, status=500)


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(login_required_json, name='dispatch')
class Disable2FAView(View):
    """
    Disable 2FA for the authenticated user.
    """
    def get(self, request):
        try:
            if not request.user.is_2fa_enabled:
                return JsonResponse({
                    'status': 'error',
                    'message': _("2FA is not enabled on your account.")
                }, status=400)
    
            disable_form = TwoFactorLoginForm()
            html_content = render_to_string('accounts/disable_2fa.html', {
                'disable_form': disable_form,
            })
            return JsonResponse({
                'status': 'success',
                'html': html_content
            }, status=200)
        except Exception as e:
            logger.exception("Error in Disable2FAView GET: %s", e)
            return JsonResponse({
                'status': 'error',
                'message': _("An error occurred while rendering the form.")
            }, status=500)
    
    @method_decorator(require_POST, name='dispatch')
    def post(self, request):
        try:
            if not request.user.is_2fa_enabled:
                return JsonResponse({
                    'status': 'error',
                    'message': _("2FA is not enabled on your account.")
                }, status=400)
    
            code = request.POST.get('code')
            if not code:
                return JsonResponse({
                    'status': 'error',
                    'message': _("Code is required.")
                }, status=400)
    
            totp = pyotp.TOTP(request.user.totp_secret)
            if totp.verify(code):
                # Disable 2FA by resetting the related fields
                request.user.totp_secret = ''
                request.user.is_2fa_enabled = False
                request.user.save()
                return JsonResponse({
                    'status': 'success',
                    'message': _("2FA has been disabled.")
                }, status=200)
    
            return JsonResponse({
                'status': 'error',
                'message': _("Invalid 2FA code.")
            }, status=400)
        except Exception as e:
            logger.exception("Unexpected error in Disable2FAView POST: %s", e)
            return JsonResponse({
                'status': 'error',
                'message': _("An unexpected error occurred.")
            }, status=500)
