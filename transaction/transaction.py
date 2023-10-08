import json

from django.core.exceptions import ValidationError

from bank import settings
from . import models, competition


def perform_transaction(
        user,
        team_number: int,
        amount: int,
        easy: int,
        medium: int,
        hard: int,
        solved_easy: int,
        solved_medium: int,
        solved_hard: int,
):
    sum_amount = calculate_amount(
        amount=amount,
        easy=easy,
        medium=medium,
        hard=hard,
        solved_easy=solved_easy,
        solved_medium=solved_medium,
        solved_hard=solved_hard,
    )

    try:
        team = models.Team.objects.get(team_number=team_number)
    except models.Team.DoesNotExist:
        raise ValidationError({'team_number': f'team number {team_number} does not exist'})

    # todo concurrency safe
    team.balance += sum_amount

    team.save()

    deposit_items = []
    withdraw_items = []

    if amount > 0:
        deposit_items.append(f"{amount} cash")
    elif amount < 0:
        withdraw_items.append(f"{-amount} cash")

    if easy > 0:
        deposit_items.append(f"{easy} easy problems")
    elif easy < 0:
        withdraw_items.append(f"{-easy} easy problems")

    if medium > 0:
        deposit_items.append(f"{medium} medium problems")
    elif medium < 0:
        withdraw_items.append(f"{-medium} medium problems")

    if hard > 0:
        deposit_items.append(f"{hard} hard problems")
    elif hard < 0:
        withdraw_items.append(f"{-hard} hard problems")

    if solved_easy > 0:
        deposit_items.append(f"{solved_easy} solved easy problems")
    elif solved_easy < 0:
        withdraw_items.append(f"{-solved_easy} solved easy problems")

    if solved_medium > 0:
        deposit_items.append(f"{solved_medium} solved medium problems")
    elif solved_medium < 0:
        withdraw_items.append(f"{-solved_medium} solved medium problems")

    if solved_hard > 0:
        deposit_items.append(f"{solved_hard} solved hard problems")
    elif solved_hard < 0:
        withdraw_items.append(f"{-solved_hard} solved hard problems")

    description_lines = []

    if len(deposit_items) != 0:
        description_lines.append('deposit ' + ", ".join(deposit_items))

    if len(withdraw_items) != 0:
        description_lines.append('withdraw ' + ", ".join(withdraw_items))

    models.Transaction(
        team=team,
        amount=sum_amount,
        balance=team.balance,
        recorded_by=user,
        recorded_at=competition.get_current_time() or settings.ARITHLAND.competition_length + 1,
        description='\n'.join(description_lines),
        is_for_interest=False,
    ).save()


def add_interest(
        team_number: int,
):
    try:
        team = models.Team.objects.get(team_number=team_number)
    except models.Team.DoesNotExist:
        raise ValidationError({'team_number': f'team number {team_number} does not exist'})

    amount = 0.1 * team.balance

    # todo concurrency safe
    team.balance += amount

    team.save()

    models.Transaction(
        team=team,
        amount=amount,
        balance=team.balance,
        recorded_by=None,
        recorded_at=competition.get_current_time() or settings.ARITHLAND.competition_length + 1,
        description="deposit interest",
        is_for_interest=True,
    ).save()


def calculate_amount(
        amount: int,
        easy: int,
        medium: int,
        hard: int,
        solved_easy: int,
        solved_medium: int,
        solved_hard: int,
) -> int:
    # change prices for unsolved problems
    easy_price = get_easy_price()
    medium_price = get_medium_price()
    hard_price = get_hard_price()
    solved_easy_price = get_solved_easy_price()
    solved_medium_price = get_solved_medium_price()
    solved_hard_price = get_solved_hard_price()

    return (
            amount +
            easy * easy_price + medium * medium_price + hard * hard_price +
            solved_easy * solved_easy_price + solved_medium * solved_medium_price + solved_hard * solved_hard_price
    )


def get_period():
    current_time = competition.get_current_time()

    if current_time is None:
        return 0

    period_length = settings.ARITHLAND.competition_length / settings.ARITHLAND.period_count

    if current_time < period_length:
        return 0

    if current_time < 2 * period_length:
        return 1

    return 2


def get_easy_price():
    return settings.ARITHLAND.base_easy_buy * (2 ** get_period())


def get_medium_price():
    return settings.ARITHLAND.base_medium_buy * (2 ** get_period())


def get_hard_price():
    return settings.ARITHLAND.base_hard_buy * (2 ** get_period())


def get_solved_easy_price():
    return 2 * settings.ARITHLAND.base_easy_sell * (2 ** get_period())


def get_solved_medium_price():
    return 2 * settings.ARITHLAND.base_medium_sell * (2 ** get_period())


def get_solved_hard_price():
    return 2 * settings.ARITHLAND.base_hard_sell * (2 ** get_period())


def calculate_max_loan(balance: int) -> int:
    return 2 * balance
