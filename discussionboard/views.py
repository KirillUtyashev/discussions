import random
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views import View
from discussionboard.models import Category, IntermediateCategory, Question, \
    Thread
from notifications.actions import show_notifications
from notifications.models import Notification
from payments.models import Subscription
from users.models import Course, User
from .actions import activate_link, add_category, add_instructor, \
    add_subcategory, comment, \
    delete, delete_category, delete_user, edit_post, endorse, \
    filter_, \
    get_thread, like, \
    load_more, pin, \
    post_answer, \
    post_thread, search, return_threads, set_password, \
    update_course_name
from .serializers import (CommentSerializer, CourseSerializer,
                          FullThreadSerializer,
                          PinnedThreadSerializer, RegularThreadSerializer,
                          AnswerSerializer,
                          CategorySerializer, SearchThreadSerializer)
from .helper_functions import (negative_response, check_status)
from users.actions import add_user


SITENAME = 'Дискуссии.ру'

ANONONYMOUS_NAMES = [
    'Анонимный ёж',
    'Анонимный заяц-русак',
    'Анонимный горностай',
    'Анонимная кабарга',
    'Анонимный сивуч'
]


class CourseView(View):
    template_name = 'discussionboard/discussion.html'
    COUNT_REGULAR_THREADS = 20
    COUNT_PINNED_THREADS = 3

    def get_methods(self, request, course, status):
        categories = cache.get_or_set(f'cached_categories_{course.code}', Category.objects.filter(course_id=course.id))
        pinned_threads, show_load_more_pinned = return_threads(Thread.objects.get_pinned_threads(course), self.COUNT_PINNED_THREADS)
        regular_threads, show_load_more_regular = return_threads(Thread.objects.get_regular_threads(course), self.COUNT_REGULAR_THREADS)
        data = {
            'course': course,
            'categories': categories,
            'pinned_threads': {'threads': pinned_threads,
                               'show_load_more': show_load_more_pinned},
            'regular_threads': {'threads': regular_threads,
                                'show_load_more': show_load_more_regular},
            'status': status,
            'sitename': SITENAME
        }
        if request.user.is_authenticated:
            data['courses'] = Course.objects.get_all_user_courses(request.user)
            data['name'] = request.user.name
            data['email'] = request.user.email
            data['unread_notifications'] = Notification.objects.user_unread_count(request.user)
        else:
            data['courses'] = Course.objects.filter(id=course.id)
            data['name'] = 'Анонимный заяц'

        return render(request, self.template_name, data)

    def post_methods(self, request, action, course):
        if action == 'get_thread':
            thread_id = request.POST.get('id')
            thread = get_thread(thread_id, request.user)
            data = {
                'thread': FullThreadSerializer(
                    thread, context={'request': request}
                ).data,
            }
            return JsonResponse(data)
        elif action == 'search':
            query = request.POST.get('query', '')
            results, show_load_more = search(query, course, self.COUNT_REGULAR_THREADS)
            return JsonResponse({
                    'threads': SearchThreadSerializer(results, many=True).data,
                    'show_load_more': show_load_more
                })
        elif action == 'filter':
            pinned_threads, show_load_more_pinned, regular_threads, show_load_more_regular, cat = filter_(request.POST.get('id'), course, self.COUNT_PINNED_THREADS, self.COUNT_REGULAR_THREADS)
            return JsonResponse({
                'pinned_threads': {'threads': PinnedThreadSerializer(pinned_threads, many=True,
                                                                     context={'request': request}
                                                                     ).data,
                                   'show_load_more': show_load_more_pinned},
                'regular_threads': {'threads': RegularThreadSerializer(regular_threads, many=True,
                                                                       context={'request': request,
                                                                                'category': cat}).data,
                                    'show_load_more': show_load_more_regular},
            })
        elif action == 'load_more':
            search_string = request.POST.get('search_string')
            type = request.POST.get('list_type')
            active_cat = request.POST.get('active_cat_filter')
            last_thread_id = request.POST.get('last_thread_id')
            threads, show_load_more, type, cat = load_more(search_string, type, last_thread_id, course, self.COUNT_REGULAR_THREADS, active_cat)
            if type == 'search':
                return JsonResponse({
                    'threads': SearchThreadSerializer(threads, many=True).data,
                    'show_load_more': show_load_more
                })
            elif type == 'regular':
                return JsonResponse({
                    'threads': RegularThreadSerializer(threads, many=True,
                                                       context={
                                                           'request': request,
                                                           'category': cat}
                                                       ).data,
                    'show_load_more': show_load_more
                })
            else:
                a = {
                    'threads': PinnedThreadSerializer(threads, many=True,
                                                      context={'request': request}
                                                      ).data,
                    'show_load_more': show_load_more
                }
                return JsonResponse(a)
        else:
            return negative_response()


class ClosedCourseView(LoginRequiredMixin, CourseView):
    login_url = '/login/'

    def get(self, request, course_slug):
        try:
            course = Course.objects.get(code=course_slug)
        except Course.DoesNotExist:
            url = reverse('discussionboard:invalid-course')
            return redirect(url)
        status = check_status(request.user, course)
        if status == '-1':
            url = reverse('discussionboard:access-restricted')
            return redirect(url)
        return super(ClosedCourseView, self).get_methods(request,
                                                         course, status)

    def post(self, request, course_slug):
        try:
            course = Course.objects.get(code=course_slug)
        except Course.DoesNotExist:
            return negative_response()
        status = check_status(request.user, course)
        if status == '-1':
            url = reverse('discussionboard:access-restricted')
            return redirect(url)
        action = request.POST.get('action')
        if not course.verify_access():
            return super(ClosedCourseView, self).post_methods(request, action,
                                                              course)
        if action == 'post':
            post_type = request.POST.get('type')
            if post_type != 'question' and post_type != 'post':
                return JsonResponse({'message': 'renew'})
            header = request.POST.get('header')
            body = request.POST.get('body')
            cat = request.POST.get('category')
            anon = request.POST.get('anonymous')
            if anon == 'false':
                name = request.user.name
            else:
                name = random.choice(ANONONYMOUS_NAMES)
            thread = post_thread(request.user, header, body, cat, name,
                                 post_type, course)
            return JsonResponse({
                'thread': FullThreadSerializer(
                    thread, context={'request': request, 'anon': anon}
                ).data
            })
        elif action == 'answer':
            return post_answer(request)
        elif action == 'like':
            return like(request)
        elif action == 'pin':
            return pin(request)
        elif action == 'delete':
            return delete(request, course)
        elif action == 'comment':
            return comment(request)
        elif action == 'endorse':
            return endorse(request, course)
        elif action == 'edit':
            return edit_post(request.POST.get('id'), request.POST.get('new_content'))
        elif action == 'get_notifications':
            return show_notifications(request)
        else:
            return super(ClosedCourseView, self).post_methods(request, action,
                                                              course)


class DemoCourseView(CourseView):

    def get(self, request):
        course = Course.objects.get(code='democls')
        status = '1'
        return super(DemoCourseView, self).get_methods(request,
                                                       course, status)

    def post(self, request):
        try:
            course = Course.objects.get(code='democls')
        except Course.DoesNotExist:
            return negative_response()
        action = request.POST.get('action')
        return super(DemoCourseView, self).post_methods(request, action, course)


class SettingsView(LoginRequiredMixin, View):
    login_url = '/login/'
    template_name = 'discussionboard/course_settings.html'

    def get(self, request, course_slug):
        course = Course.objects.filter(code=course_slug).only('code', 'name', 'categories', 'password', 'is_active_link').first()
        if not course:
            url = reverse('discussionboard:invalid-course')
            return redirect(url)
        status = Course.objects.status(request.user, course)
        if status == '0' or status == '-1':
            url = reverse('discussionboard:access-restricted')
            return redirect(url)
        students = cache.get_or_set(f'students_{course.code}', User.objects.filter(courses_joined__id=course.id).only('email', 'name'))
        instructors = cache.get_or_set(f'instructors_{course.code}', User.objects.filter(courses_instructed__id=course.id).only('email', 'name'))
        invite_link = course.get_invite_link()
        data = {
                'course': course,
                'sitename': SITENAME,
                'status': status,
                'name': request.user.name,
                'email': request.user.email,
                'students': students,
                'instructors': instructors,
                'categories': cache.get_or_set(f'cached_categories_{course.code}', Category.objects.filter(course_id=course.id)),
                'invite_link': invite_link,
                'unread_notifications': Notification.objects.user_unread_count(request.user)
        }
        return render(request, self.template_name, data)

    def post(self, request, course_slug):
        try:
            course = Course.objects.get(code=course_slug)
        except Course.DoesNotExist:
            url = reverse('discussionboard:invalid-course')
            return redirect(url)
        action = request.POST.get('action')
        if action == 'update_course_name':
            return update_course_name(course, request.POST.get('new_name'))
        elif action == 'activate_link':
            return activate_link(course, request.POST.get('active'))
        elif action == 'set_password':
            return set_password(course, request.POST.get('password'))
        elif action == 'add_category':
            return add_category(course, request.POST.get('name'))
        elif action == 'add_subcategory':
            return add_subcategory(course, request.POST.get('cat'), request.POST.get('name'))
        elif action == 'add_instructor':
            return add_instructor(course, request.POST.get('name'))
        elif action == 'delete_user':
            return delete_user(course, request.POST.get('user_id'))
        elif action == 'get_notifications':
            return show_notifications(request)
        elif action == 'delete_cat':
            return delete_category(request)


class InvalidCourseView(LoginRequiredMixin, View):
    login_url = '/login/'
    template_name = 'discussionboard/course_does_not_exist.html'

    def get(self, request):
        return render(request, self.template_name)


class AccessRestrictedView(LoginRequiredMixin, View):
    login_url = '/login/'
    template_name = 'discussionboard/access_restricted.html'

    def get(self, request):
        return render(request, self.template_name)


class JoinCourseView(LoginRequiredMixin, View):
    login_url = '/login/'
    template_name = 'discussionboard/access_restricted.html'

    def get(self, request, course_slug):
        try:
            course = Course.objects.get(code=course_slug)
        except Course.DoesNotExist:
            url = reverse('discussionboard:invalid-course')
            return redirect(url)
        if course.is_active_link is False:
            url = reverse('discussionboard:access-restricted')
            return redirect(url)
        add_user(course, request.user)
        return redirect(course.get_absolute_url())
