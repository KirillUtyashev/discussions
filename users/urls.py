from django.contrib.auth.views import PasswordChangeView, \
    PasswordResetConfirmView
from django.urls import path, reverse_lazy
from .views import (RegisterUser, LoginUser, LogoutView,
                    home,
                    DashboardView,
                    SettingsView, HelpView, privacy,
                    universities, contacts, about, confirm_email)
from django.views.generic.base import RedirectView, TemplateView
app_name = 'users'

favicon_view = RedirectView.as_view(url='/static/img/favicon.svg', permanent=True)

urlpatterns = [
    path('login/', LoginUser.as_view(), name='login'),
    path('', home, name='about'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('settings/', SettingsView.as_view(), name='settings'),
    path('help/', HelpView.as_view(), name='help'),
    path('password-reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(
             template_name="users/password_reset_confirm.html",
             success_url=reverse_lazy('users:login')
         ),
         name='password_reset_confirm'),
    path('activate/<uidb64>/<token>/', confirm_email, name='confirm-email'),
    path('change/', PasswordChangeView.as_view(), name='change'),
    path('universities/', universities, name='universities'),
    path('contact/', contacts, name='contact'),
    path('about/', about, name='about_us'),
    path('privacy/', privacy, name='privacy'),
    path('robots.txt', TemplateView.as_view(template_name="users/robots.txt", content_type="text/plain")),
    path("static/img/favicon.svg", favicon_view),
]
