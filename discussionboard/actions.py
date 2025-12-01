import random
from django.contrib.postgres.search import SearchVector, SearchQuery, \
    SearchRank, TrigramSimilarity, TrigramWordSimilarity
from django.http import JsonResponse
from discussionboard.models import Answer, Category, IntermediateCategory, \
    IntermediatePost, Question, SubCategory, Thread
from discussionboard.serializers import (AnswerSerializer, CommentSerializer,
                                         RegularThreadSerializer,
                                         PinnedThreadSerializer)
from users.helper_functions import negative_response
from users.models import User
from notifications.tasks import send_post_email, notify_user
from django.core.cache import cache


ANONONYMOUS_NAMES = [
    'Анонимный ёж',
    'Анонимный заяц-русак',
    'Анонимный горностай',
    'Анонимная кабарга',
    'Анонимный сивуч'
]


# Helper functions
def check_if_admin(user, course):
    if (course.instructors.filter(email=user.email).exists or
            course.author.email == user.email):
        return
    return negative_response()


def return_threads(threads, count_local):
    count_global = threads.count()
    if count_global > count_local:
        threads_to_return = threads[:count_local]
        show_load_more = True
    else:
        threads_to_return = threads[:count_global]
        show_load_more = False
    return threads_to_return, show_load_more


def like_model(request) -> JsonResponse:
    try:
        obj = IntermediatePost.objects.get(id=request.POST.get('id'))
    except IntermediatePost.DoesNotExist:
        return negative_response()
    if obj.likes.filter(id=request.user.id).exists():
        obj.likes.remove(request.user)
    else:
        obj.likes.add(request.user)
    return JsonResponse({
        'message': '1'
    })

# User interactions -> to be connected with Websocket


def post_thread(user, header, body, cat, name, post_type, course):
    current_week = course.weeks.last()
    question = Question.objects.create(author=user,
                                       body=body,
                                       author_name=name)
    thread = Thread.objects.create(course=course,
                                   title=header,
                                   id_within_course=course.get_thread_id(),
                                   category=IntermediateCategory.objects.get(
                                       id=cat
                                   ),
                                   question=question,
                                   type=post_type,
                                   week_id=current_week.id)
    if thread.type == 'post':
        send_post_email.delay(course.id, thread.id)
    return thread


def post_answer(request):
    try:
        thread = Thread.objects.get(id=request.POST.get('thread'))
    except Thread.DoesNotExist:
        return negative_response()
    if thread.type == 'post':
        return negative_response()
    anon = request.POST.get('anonymous')
    if anon == 'false':
        name = request.user.name
    else:
        name = random.choice(ANONONYMOUS_NAMES)
    ans = Answer.objects.create(body=request.POST.get('body'),
                                author_id=request.user.id,
                                thread_id=thread.id,
                                author_name=name)
    message = f'<b>{ans.author.name}</b> ответил(а) на ваш вопрос в дискуссии: {thread.title}'
    notify_user.delay(ans.thread.question.author.id, message, ans.thread.id)
    return JsonResponse({
        'answer': AnswerSerializer(
            ans, context={'request': request}
        ).data
    })


def like(request):
    if request.POST.get('id'):
        return like_model(request)
    else:
        return negative_response()


def pin(request):
    try:
        thread = Thread.objects.get(id=request.POST.get('id'))
    except Thread.DoesNotExist:
        return negative_response()
    if thread.is_pinned is True:
        thread.is_pinned = False
    else:
        thread.is_pinned = True
    thread.save(update_fields=['is_pinned'])
    return JsonResponse({
        'message': '1'
    })


def delete(request, course):
    check = check_if_admin(request.user, course)
    if check:
        return check
    if (Question.objects.filter(id=request.POST.get('id')).delete()[0] != 0 or
            Answer.objects.filter(id=request.POST.get('id')).delete()[0] != 0 or
            IntermediatePost.objects.filter(id=request.POST.get('id')).delete()[0] != 0):

        return JsonResponse({
            'message': '1'
        })
    return negative_response()


def comment(request):
    anon = request.POST.get('anonymous')
    if anon == 'false':
        name = request.user.name
    else:
        name = random.choice(ANONONYMOUS_NAMES)
    try:
        parent_post = IntermediatePost.objects.get(id=request.POST.get('target_id'))
    except IntermediatePost.DoesNotExist:
        return negative_response()
    thread_id = request.POST.get('thread_id')
    new_comment = parent_post.comments.create(author_id=request.user.id, author_name=name,
                                              body=request.POST.get('body'),
                                              post_id=parent_post.id,
                                              thread_id=thread_id)
    message = f'<b>{name}</b> прокомментировал(а) ваш пост в дискуссии: {Thread.objects.get(id=thread_id).title}'
    notify_user.delay(parent_post.author.id, message, thread_id)
    return JsonResponse({
        'comment': CommentSerializer(new_comment, context={'request': request}).data,
        'message': '1'
    })


def endorse(request, course):
    check = check_if_admin(request.user, course)
    if check:
        return check
    post_id = request.POST.get('id')
    post = Answer.objects.filter(id=post_id)
    if not post:
        post = IntermediatePost.objects.filter(id=post_id)
    if post[0].endorsed_by:
        post.update(endorsed_by=None)
    else:
        post.update(endorsed_by=request.user)
    return JsonResponse({
        'message': '1'
    })


def edit_post(post_id, new_content):
    try:
        post = IntermediatePost.objects.filter(id=post_id)
    except IntermediatePost.DoesNotExist:
        return negative_response()
    post.update(body=new_content)
    return JsonResponse({
        'message': '1',
        'body': post[0].body
    })


# Getting, finding and filtering threads


def get_thread(thread_id, user):
    try:
        thread = Thread.objects.get(id=thread_id)
    except Thread.DoesNotExist:
        return negative_response()
    if user.is_authenticated:
        thread.add_viewer(user)
        thread.notifications.filter(user=user).update(viewed=True)
    else:
        thread.add_viewer(None)
    return thread


def return_search_result(query, course):
    A = 1.0
    B = 0.4
    search_ = Thread.objects.annotate(
        similarity=(A / (A + B) * TrigramSimilarity('title', query)
                    + B / (A + B) * TrigramWordSimilarity(query, 'question__body'))
    ).filter(similarity__gte=0.1, course=course).order_by('-similarity')
    if not search_:
        search_vector = SearchVector('title', 'question__body')
        search_query = SearchQuery(query)
        search_ = Thread.objects.filter(course=course).annotate(search=search_vector, rank=SearchRank(search_vector, search_query)).filter(search=search_query).order_by('-rank')
    return search_


def search(query, course, count_regular):
    results, show_load_more = return_threads(return_search_result(query, course), count_regular)
    return results, show_load_more


def filter_(id_, course, count_pinned, count_regular):
    if not id_:
        cat = None
        pinned_threads, show_load_more_pinned = return_threads(Thread.objects.get_pinned_threads(course), count_pinned)
        regular_threads, show_load_more_regular = return_threads(Thread.objects.get_regular_threads(course), count_regular)
    else:
        try:
            cat = Category.objects.get(id=id_)
        except Category.DoesNotExist:
            try:
                cat = SubCategory.objects.get(id=id_)
            except SubCategory.DoesNotExist:
                return negative_response()
        get_pinned_threads = Thread.objects.get_pinned_threads(course).filter(category=cat)
        get_regular_threads = Thread.objects.get_regular_threads(course).filter(category=cat)
        if type(cat) is Category:
            for subcategory in cat.subcategories.all():
                get_pinned_threads = get_pinned_threads.union(Thread.objects.get_pinned_threads(course).filter(category=subcategory)).order_by('-question')
                get_regular_threads = get_regular_threads.union(Thread.objects.get_regular_threads(course).filter(category=subcategory)).order_by('-question')
        pinned_threads, show_load_more_pinned = return_threads(get_pinned_threads, count_pinned)
        regular_threads, show_load_more_regular = return_threads(get_regular_threads, count_regular)
    return pinned_threads, show_load_more_pinned, regular_threads, show_load_more_regular, cat


def load_more_search(query, course, count_regular, last_thread_id):
    search_ = return_search_result(query, course)
    list_search = [thread.pk for thread in search_]
    last_thread_index = list_search.index(int(last_thread_id))
    if len(list_search) - last_thread_index < count_regular:
        threads_ids = list_search[last_thread_index + 1:]
        show_load_more = False
    else:
        threads_ids = list_search[last_thread_index + 1:last_thread_index + count_regular]
        show_load_more = True
    result = Thread.objects.filter(course=course, id__in=threads_ids)
    return result, show_load_more, 'search', None


def load_more_regular(course, count_regular, cat, last_thread_id):
    if cat:
        result = Thread.objects.get_regular_threads(course).filter(id__lt=last_thread_id, category=cat)
        threads, show_load_more = return_threads(result, count_regular)
    else:
        cat = None
        result = Thread.objects.get_regular_threads(course).filter(id__lt=last_thread_id)
        threads, show_load_more = return_threads(result, count_regular)
    return threads, show_load_more, 'regular', cat


def load_more_pinned(course, cat, last_thread_id):
    if cat:
        result = Thread.objects.get_pinned_threads(course).filter(id__lt=last_thread_id, category=cat)
        threads, show_load_more = result, False
    else:
        result = Thread.objects.get_pinned_threads(course).filter(id__lt=last_thread_id)
        threads, show_load_more = result, False
    return threads, show_load_more, 'pinned', None


def load_more(search_string, type, last_thread_id, course, count_regular, cat):
    if search_string:
        return load_more_search(search_string, course, count_regular, last_thread_id)
    else:
        if type == 'regular':
            return load_more_regular(course, count_regular, cat, last_thread_id)
        elif type == 'pinned':
            return load_more_pinned(course, cat, last_thread_id)
        else:
            return negative_response()


def update_course_name(course, name):
    course.name = name
    course.save(update_fields=['name'])
    return JsonResponse({'message': '1'})


def activate_link(course, active):
    if active == '0':
        course.is_active_link = False
    elif active == '1':
        course.is_active_link = True
    else:
        return negative_response()
    course.save(update_fields=['is_active_link'])
    return JsonResponse({'message': '1'})


def set_password(course, password):
    course.password = password
    course.save(update_fields=['password'])
    return JsonResponse({'message': '1'})


def add_category(course, tag):
    if course.categories.filter(tag=tag).exists():
        return JsonResponse({
            'message': '0'
        })
    category = course.categories.create(tag=tag)
    cache.delete(f'cached_categories_{course.code}')
    return JsonResponse({
        'message': '1',
        'name': category.tag,
        'id': category.id
    })


def add_subcategory(course, parent_category_id, tag):
    if course.subcategories.filter(tag=tag).exists():
        return JsonResponse({
            'message': '0'
        })
    subcategory = course.subcategories.create(tag=tag, parent_category_id=parent_category_id)
    cache.delete(f'cached_categories_{course.code}')
    return JsonResponse({
        'message': '1',
        'name': subcategory.tag,
        'id': subcategory.id
    })


def add_instructor(course, email):
    if not User.objects.filter(email=email).exists():
        return negative_response()
    elif course.students.filter(email=email).exists():
        course.students.remove(User.objects.get(email=email))
        cache.delete(f'students_{course.code}')
    elif course.instructors.filter(email=email).exists():
        return JsonResponse({'message': 2})
    instructor = User.objects.get(email=email)
    course.instructors.add(instructor)
    cache.delete(f'instructors_{course.code}')
    cache.delete(f'{instructor.id}_courses')
    return JsonResponse({
        'message': '1',
        'name': instructor.name,
        'email': instructor.email,
        'id': instructor.id
    })


def delete_user(course, user_id):
    if course.students.remove(User.objects.get(id=user_id)):
        cache.delete(f'students_{course.code}')
        cache.delete(f'{user_id}_courses')
        return JsonResponse({'message': '1'})
    else:
        course.instructors.remove(User.objects.get(id=user_id))
        cache.delete(f'instructors_{course.code}')
        cache.delete(f'{user_id}_courses')
        return JsonResponse({'message': '1'})


def delete_category(request):
    category_to_delete = Category.objects.get(id=request.POST.get('cat_id'))
    new_category = Category.objects.get(id=request.POST.get('new_cat_id'))
    Thread.objects.filter(category=category_to_delete).update(category=new_category)
    category_to_delete.delete()
    cache.delete(f'cached_categories_{new_category.course.code}')
    cache.delete(f'cached_pinned_threads_{new_category.course.code}')
    cache.delete(f'cached_regular_threads_{new_category.course.code}')
    return JsonResponse({'message': '1'})
