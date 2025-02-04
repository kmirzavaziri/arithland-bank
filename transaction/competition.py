import time

from bank import settings
from . import models, config_keys


def start(teams_count: int):
    exists = False
    try:
        models.Config.objects.get(key=config_keys.START_TIME)
        exists = True
    except models.Config.DoesNotExist:
        pass

    if exists:
        raise ValueError("a competition is already started")

    models.Config.objects.all().delete()
    models.Team.objects.all().delete()
    models.Transaction.objects.all().delete()

    models.Team.objects.bulk_create([
        models.Team(team_number=team_number, balance=0) for team_number in range(1, teams_count + 1)
    ])

    models.Config(key=config_keys.START_TIME, value=str(int(time.time()))).save()


def finish():
    try:
        models.Config.objects.get(key=config_keys.START_TIME).delete()
    except models.Config.DoesNotExist:
        raise ValueError("no competition is running")


def get_current_time():
    try:
        start_time = models.Config.objects.get(key=config_keys.START_TIME).value
        return int(time.time()) - int(start_time)
    except models.Config.DoesNotExist:
        return None


def is_near_end():
    return get_current_time() is not None and get_current_time() >= (1 - 1 / (2 * settings.ARITHLAND.period_count)) * settings.ARITHLAND.competition_length
