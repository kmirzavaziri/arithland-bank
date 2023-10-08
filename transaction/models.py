from django.conf import settings
from django.db import models


class Team(models.Model):
    team_number = models.IntegerField(unique=True, primary_key=True)
    balance = models.BigIntegerField()


class Config(models.Model):
    key = models.CharField(unique=True, primary_key=True, max_length=100)
    value = models.TextField()


class Transaction(models.Model):
    team = models.ForeignKey(to=Team, on_delete=models.CASCADE)
    amount = models.BigIntegerField()
    balance = models.BigIntegerField()
    description = models.TextField()
    is_for_interest = models.BooleanField()
    recorded_by = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    recorded_at = models.IntegerField()
