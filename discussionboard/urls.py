from django.urls import path
from django.views.generic import RedirectView
from .views import AccessRestrictedView, DemoCourseView, InvalidCourseView, \
    JoinCourseView, SettingsView, ClosedCourseView

app_name = 'discussionboard'

urlpatterns = [
    path('democls/discussion/', DemoCourseView.as_view(), name='demo-course'),
    path('<slug:course_slug>/discussion/', ClosedCourseView.as_view(), name='course'),
    path('<slug:course_slug>/settings/', SettingsView.as_view(), name='settings'),
    path('<slug:course_slug>/join', JoinCourseView.as_view(), name='join-course'),
    path('<slug:course_slug>/', RedirectView.as_view(pattern_name='discussionboard:course', permanent=False)),
    path('invalid-course', InvalidCourseView.as_view(), name='invalid-course'),
    path('access-restricted', AccessRestrictedView.as_view(), name='access-restricted')
]
