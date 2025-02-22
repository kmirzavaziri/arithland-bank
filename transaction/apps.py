import os

from django.apps import AppConfig


class TransactionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "transaction"

    def ready(self):
        from . import tasks

        if os.environ.get("RUN_MAIN", None) != "true":
            tasks.start_scheduler()


# TODO add refund option (rollback or whatever)
