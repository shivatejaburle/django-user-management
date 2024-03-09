from django.views.generic import View, FormView
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404

# Forms
from accounts.forms import (
    SignInViaEmailForm, SignInViaEmailOrUsernameForm, 
    SignInViaUsernameForm, SignUpForm,
)

from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth import login, REDIRECT_FIELD_NAME, authenticate
from django.utils.http import url_has_allowed_host_and_scheme as is_safe_url
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LogoutView as BaseLogoutView
)
from django.utils.crypto import get_random_string

# Models
from accounts.models import Activation

from .utils import (
    send_activation_email
)

from django.contrib import messages

# Guest View
class GuestOnlyView(View):
    def dispatch(self, request, *args, **kwargs):
        # Redirect to the index page if the user already authenticated
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)

        return super().dispatch(request, *args, **kwargs)
    
# Login View
class LogInView(GuestOnlyView, FormView):
    template_name = 'accounts/log_in.html'
    success_url = settings.LOGIN_REDIRECT_URL

    @staticmethod
    def get_form_class(**kwargs):
        if settings.DISABLE_USERNAME or settings.LOGIN_VIA_EMAIL:
            return SignInViaEmailForm

        if settings.LOGIN_VIA_EMAIL_OR_USERNAME:
            return SignInViaEmailOrUsernameForm

        return SignInViaUsernameForm

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        # Sets a test cookie to make sure the user has cookies enabled
        request.session.set_test_cookie()

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        request = self.request

        # If the test cookie worked, go ahead and delete it since its no longer needed
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()

        # The default Django's "remember me" lifetime is 2 weeks and can be changed by modifying
        # the SESSION_COOKIE_AGE settings' option.
        if settings.USE_REMEMBER_ME:
            if not form.cleaned_data['remember_me']:
                request.session.set_expiry(0)

        login(request, form.user_cache)

        redirect_to = request.POST.get(REDIRECT_FIELD_NAME, request.GET.get(REDIRECT_FIELD_NAME))
        url_is_safe = is_safe_url(redirect_to, allowed_hosts=request.get_host(), require_https=request.is_secure())

        if url_is_safe:
            return redirect(redirect_to)

        return redirect(self.success_url)

# Logout
class LogOutView(LoginRequiredMixin, BaseLogoutView):
    template_name = "accounts/log_out.html"

# Signup View
class SignUpView(GuestOnlyView, FormView):
    template_name = "accounts/sign_up.html"
    form_class = SignUpForm
    success_url = 'index'

    def form_valid(self, form):
        request = self.request
        user = form.save(commit=False)

        if settings.DISABLE_USERNAME:
            # Set a temporary username
            user.username = get_random_string()
        else:
            user.username = form.cleaned_data["username"]

        if settings.ENABLE_USER_ACTIVATION:
            user.is_active = False

         # Create a user record
        user.save()

        # Change the username to the "user_ID" form
        if settings.DISABLE_USERNAME:
            user.username = f'user_{user.id}'
            user.save()
        
        if settings.ENABLE_USER_ACTIVATION:
            code = get_random_string(20)
            # Object for Activation Model
            actObj = Activation()
            actObj.code = code
            actObj.user = user
            actObj.save()

            send_activation_email(request, user.email, code)
            messages.success(request, "Please check your email to activate your account.")
        else:
            raw_password = form.cleaned_data['password1']

            user = authenticate(username = user.username, password=raw_password)
            login(request, user)
            
            messages.success(request, 'Your account was successfully created. You are now logged in.')
        
        return redirect(self.success_url)
    
class ActivateView(View):
    @staticmethod
    def get(request, code):
        activate = get_object_or_404(Activation, code=code)

        # Activate User Account
        user_account = activate.user
        user_account.is_active = True
        user_account.save()

        # Remove the activation record
        activate.delete()

        messages.success(request, "Account has been activated!")

        return redirect('accounts:log_in')