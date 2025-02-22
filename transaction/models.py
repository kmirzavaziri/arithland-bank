from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Competition(models.Model):
    slug = models.CharField(max_length=100, unique=True)

    start_time = models.DateTimeField()

    teams_count = models.IntegerField()

    interest_range_length = models.IntegerField(default=10, help_text="in minutes")
    competition_length = models.IntegerField(default=90, help_text="in minutes")
    period_count = models.IntegerField(default=3, help_text="The number of inflation periods")

    base_easy_sell = models.FloatField(default=100)
    base_medium_sell = models.FloatField(default=300)
    base_hard_sell = models.FloatField(default=500)

    base_easy_buy = models.FloatField(default=300 / 4)
    base_medium_buy = models.FloatField(default=500 / 4)
    base_hard_buy = models.FloatField(default=800 / 4)

    @property
    def interest_range_length_sec(self):
        return self.interest_range_length * 60

    @property
    def competition_length_sec(self):
        return self.competition_length * 60

    def is_ongoing(self):
        return 0 <= self.get_current_time() <= self.competition_length_sec

    def get_current_time(self):
        return int((timezone.now() - self.start_time).total_seconds())

    def is_near_end(self):
        current_time = self.get_current_time()
        return (
            current_time is not None and current_time >= (1 - 1 / (2 * self.period_count)) * self.competition_length_sec
        )

    def calculate_amount(
        self,
        amount: int,
        easy: int,
        medium: int,
        hard: int,
        solved_easy: int,
        solved_medium: int,
        solved_hard: int,
    ) -> int:
        return (
            amount
            + easy * self.get_easy_price()
            + medium * self.get_medium_price()
            + hard * self.get_hard_price()
            + solved_easy * self.get_solved_easy_price()
            + solved_medium * self.get_solved_medium_price()
            + solved_hard * self.get_solved_hard_price()
        )

    def get_period(self):
        current_time = self.get_current_time()

        if current_time is None:
            return 0

        period_length = self.competition_length_sec / self.period_count

        if current_time < period_length:
            return 0

        if current_time < 2 * period_length:
            return 1

        return 2

    def get_easy_price(self):
        return self.base_easy_buy * (2 ** self.get_period())

    def get_medium_price(self):
        return self.base_medium_buy * (2 ** self.get_period())

    def get_hard_price(self):
        return self.base_hard_buy * (2 ** self.get_period())

    def get_solved_easy_price(self):
        return 2 * self.base_easy_sell * (2 ** self.get_period())

    def get_solved_medium_price(self):
        return 2 * self.base_medium_sell * (2 ** self.get_period())

    def get_solved_hard_price(self):
        return 2 * self.base_hard_sell * (2 ** self.get_period())

    def calculate_max_loan(self, balance: int) -> int:
        return 2 * balance

    def __str__(self):
        return self.slug


class User(AbstractUser):
    competition = models.ForeignKey(Competition, on_delete=models.SET_NULL, null=True, blank=True)


class ActiveTeamManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deactivated=False)


class Team(models.Model):
    objects = ActiveTeamManager()
    all_objects = models.Manager()

    team_number = models.IntegerField()
    balance = models.BigIntegerField()
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    deactivated = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.team_number}"

    class Meta:
        unique_together = ("competition", "team_number")


class Transaction(models.Model):
    team = models.ForeignKey(to=Team, on_delete=models.CASCADE)
    amount = models.BigIntegerField()
    balance = models.BigIntegerField()
    description = models.TextField()
    is_for_interest = models.BooleanField()
    recorded_by = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    recorded_at = models.IntegerField()

    def __str__(self):
        return f"Teem {self.team} {signed(self.amount)} ({self.balance})"


def signed(amount):
    return f"+{amount}" if amount > 0 else amount
