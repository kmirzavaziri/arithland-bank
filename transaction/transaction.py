from django.core.exceptions import ValidationError

from transaction import models
from transaction.models import Team


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
    sum_amount = user.competition.calculate_amount(
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
        raise ValidationError({"team_number": f"team number {team_number} does not exist"})

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
        description_lines.append("deposit " + ", ".join(deposit_items))

    if len(withdraw_items) != 0:
        description_lines.append("withdraw " + ", ".join(withdraw_items))

    models.Transaction(
        team=team,
        amount=sum_amount,
        balance=team.balance,
        recorded_by=user,
        recorded_at=team.competition.get_current_time(),
        description="\n".join(description_lines),
        is_for_interest=False,
    ).save()


def add_interest(team: Team):
    amount = 0.1 * team.balance

    # todo concurrency safe
    team.balance += amount

    team.save()

    models.Transaction(
        team=team,
        amount=amount,
        balance=team.balance,
        recorded_by=None,
        recorded_at=team.competition.get_current_time(),
        description="deposit interest",
        is_for_interest=True,
    ).save()
