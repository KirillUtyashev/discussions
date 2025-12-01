from django.apps import AppConfig

# Register the task to be executed


class DiscussionboardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "discussionboard"

    def ready(self):
        import discussionboard.signals
