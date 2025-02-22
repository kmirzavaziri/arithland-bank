import logging
import threading
import time

from schedule import Scheduler

from transaction.models import Competition
from transaction.models import Team
from transaction.models import Transaction
from transaction.transaction import add_interest

logger = logging.getLogger(__name__)


def check():
    for competition in Competition.objects.all():
        if not competition.is_ongoing():
            continue

        current_time = competition.get_current_time()

        interest_range_start_time = (
            current_time // competition.interest_range_length_sec * competition.interest_range_length_sec
        )
        interest_range_end_time = interest_range_start_time + competition.interest_range_length_sec

        for team in Team.objects.all():
            interest_added = Transaction.objects.filter(
                team=team,
                recorded_at__gte=interest_range_start_time,
                recorded_at__lte=interest_range_end_time,
                is_for_interest=True,
            ).exists()
            if not interest_added:
                add_interest(team)
                logger.info(
                    "calculated and deposited interest for team %s competition %s",
                    team.team_number,
                    competition.slug,
                )


def run_continuously(self, interval=1):
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                try:
                    self.run_pending()
                except Exception:
                    logger.exception("scheduler encountered an error")
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.setDaemon(True)
    continuous_thread.start()

    return cease_continuous_run


Scheduler.run_continuously = run_continuously  # type: ignore[attr-defined]


def start_scheduler():
    scheduler = Scheduler()
    scheduler.every().second.do(check)
    scheduler.run_continuously()
