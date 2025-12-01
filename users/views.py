from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.utils.encoding import force_str
from .tokens import account_activation_token
from notifications.actions import show_notifications
from .actions import change_email, change_password, change_profile, \
    create_course, \
    generate_default_data, \
    join_course, \
    reset_password, unenroll, switch_renewal, send_confirmation_email
from .forms import RegisterUserForm
from django.views import View
from django.contrib.auth.forms import PasswordResetForm
from payments.models import Subscription
from users.actions import register_user
from users.models import Course, User
from django.utils.http import urlsafe_base64_decode
from django.http import Http404
from django.conf import settings
from django.http import FileResponse, HttpRequest, HttpResponse
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET

SITENAME = 'Дискуссии.ру'


# @require_GET
# @cache_control(max_age=60 * 60 * 24, immutable=True, public=True)  # one day
# def favicon(request: HttpRequest) -> HttpResponse:
#     file = (settings.BASE_DIR / "static/img" / "favicon.svg").open("rb")
#     return FileResponse(file)


def custom_404(request, exception):
    return render(request, 'users/404.html', status=404)


def home(request, *args, **kwargs):
    data = {
        'sitename': SITENAME,
        'democlass': Course.objects.get(is_demo=True).get_absolute_url()
    }
    return render(request, 'users/index.html', data)


def privacy(request, *args, **kwargs):
    data = {'sitename': SITENAME}
    return render(request, 'users/privacy.html', data)


def about(request, *args, **kwargs):
    data = {'sitename': SITENAME}
    return render(request, 'users/about.html', data)


def universities(request, *args, **kwargs):
    data = {'sitename': SITENAME}
    return render(request, 'users/universities.html', data)


def contacts(request, *args, **kwargs):
    data = {'sitename': SITENAME}
    return render(request, 'users/contacts.html', data)


def confirm_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        if user.email_is_verified:
            return redirect('/dashboard/')
        user.email_is_verified = True
        user.save(update_fields=['email_is_verified'])
        return render(request, 'users/verification-success.html')
    else:
        raise Http404()


class RegisterUser(View):
    model = User
    form_class = RegisterUserForm
    template_name = 'users/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/dashboard/')
        data = {'sitename': SITENAME}
        return render(request, self.template_name, data)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            register_user(email, form.cleaned_data['name'], password)
            user = authenticate(request, username=email, password=password)
            login(request, user)
            send_confirmation_email(user.email)
            return JsonResponse({'message': '1'})
        else:
            return JsonResponse({
                'message': '0'
            })


class LoginUser(View):
    template_name = 'users/login.html'
    password_reset_form = PasswordResetForm
    subject_template_name = "users/password_reset_subject.txt"
    email_template_name = "users/password_reset_email.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/dashboard/')
        data = {'sitename': SITENAME}
        return render(request, self.template_name, data)

    def post(self, request):
        action = request.POST.get('action')
        if action == 'login':
            email = request.POST['email'].strip()
            if not User.objects.filter(email=email).exists():
                return JsonResponse({
                    'message': '2'
                })
            password = request.POST['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({
                    'message': '1',
                })
            else:
                return JsonResponse({
                    'message': '0'}
                )
        elif action == 'reset':
            password_form = self.password_reset_form(request.POST)
            if password_form.is_valid():
                return reset_password(password_form.cleaned_data['email'])
            else:
                return JsonResponse({'message': '0'})
        else:
            return JsonResponse({
                'message': '-1'
            })


class LogoutView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        logout(request)
        return redirect('/login/')


class DashboardView(LoginRequiredMixin, View):
    login_url = '/login/'
    template_name = 'users/dashboard.html'

    def get(self, request):
        data = generate_default_data(request)
        data['is_verified'] = request.user.email_is_verified
        return render(request, 'users/dashboard.html', data)

    def post(self, request):
        action = request.POST.get('action')
        if action == 'join':
            return join_course(request)
        elif action == 'create':
            return create_course(request)
        elif action == 'get_notifications':
            return show_notifications(request)
        else:
            return JsonResponse({
                'message': '-1'
            })


class SettingsView(LoginRequiredMixin, View):
    login_url = '/login/'
    template_name = 'users/settings.html'

    def get(self, request):
        data = generate_default_data(request)
        try:
            current_subscription = request.user.subscriptions.get(active=True)
            expiry_date = current_subscription.expires.strftime('%d %B %Y')
            renewal = current_subscription.renewal
        except Subscription.DoesNotExist:
            expiry_date = None
            renewal = None
        data['expiry_date'] = expiry_date
        data['renewal'] = renewal
        data['is_verified'] = request.user.email_is_verified
        return render(request, self.template_name, data)

    def post(self, request):
        action = request.POST.get('action')
        if action == 'change_password':
            return change_password(request)
        elif action == 'change_email':
            return change_email(request)
        elif action == 'change_profile':
            return change_profile(request)
        elif action == 'unenroll':
            return unenroll(request)
        elif action == 'get_notifications':
            return show_notifications(request)
        elif action == 'switch_renewal':
            renewal = request.POST.get('renewal')
            res = switch_renewal(renewal, request.user)
            if not res:
                return JsonResponse({
                    'message': '1'
                })
            return res
        elif action == 'send_link':
            email = request.user.email
            send_confirmation_email(email)
            return JsonResponse({
                'message': '1'
            })
        else:
            return JsonResponse({
                'message': '-1'
            })


class HelpView(LoginRequiredMixin, View):
    login_url = '/login/'
    template_name = 'users/contacts.html'

    def get(self, request):
        data = {'sitanme': SITENAME}
        return render(request, self.template_name, data)
