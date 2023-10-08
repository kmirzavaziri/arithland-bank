from schedule import Scheduler
import threading
import time

from bank import settings
from . import competition, models, transaction


def check():
    current_time = competition.get_current_time()

    if current_time is None:
        return

    if current_time > settings.ARITHLAND.competition_length:
        competition.finish()

    interest_range_start_time = (
            current_time // settings.ARITHLAND.interest_range_length * settings.ARITHLAND.interest_range_length
    )
    interest_range_end_time = interest_range_start_time + settings.ARITHLAND.interest_range_length

    for team in models.Team.objects.all():
        interest_added = models.Transaction.objects.filter(
            team__team_number=team.team_number,
            recorded_at__gte=interest_range_start_time,
            recorded_at__lte=interest_range_end_time,
        ).exists()
        if not interest_added:
            transaction.add_interest(team.team_number)


def run_continuously(self, interval=1):
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):

        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                self.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.setDaemon(True)
    continuous_thread.start()
    return cease_continuous_run


Scheduler.run_continuously = run_continuously


def start_scheduler():
    scheduler = Scheduler()
    scheduler.every().second.do(check)
    scheduler.run_continuously()
