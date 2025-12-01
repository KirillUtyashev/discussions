from django.contrib import admin

from discussionboard.models import Category, Question, Thread, Week, Answer, Comment

admin.site.register(Thread)
admin.site.register(Week)
admin.site.register(Question)
admin.site.register(Category)
admin.site.register(Answer)
admin.site.register(Comment)
