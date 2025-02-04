from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy

from . import models, transaction, widgets, competition


class TransactionForm(forms.Form):
    team_number = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={'placeholder': 'شماره تیم'}),
    )
    team_balance = forms.Field(
        required=False,
        widget=widgets.RequestWidget(target_input='team_number', endpoint=reverse_lazy('teams__get_balance_by_number')),
    )
    amount = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'مقدار'}),
    )
    solved_easy = forms.IntegerField(
        min_value=0,
        required=False,
        label='SE',
        widget=forms.NumberInput(attrs={'placeholder': 'ساده حل‌شده'}),
    )
    solved_medium = forms.IntegerField(
        min_value=0,
        required=False,
        label='SM',
        widget=forms.NumberInput(attrs={'placeholder': 'متوسط حل‌شده'}),
    )
    solved_hard = forms.IntegerField(
        min_value=0,
        required=False,
        label='SH',
        widget=forms.NumberInput(attrs={'placeholder': 'سخت حل‌شده'}),
    )
    easy = forms.IntegerField(
        min_value=0,
        required=False,
        label='E',
        widget=forms.NumberInput(attrs={'placeholder': 'ساده حل‌نشده'}),
    )
    medium = forms.IntegerField(
        min_value=0,
        required=False,
        label='M',
        widget=forms.NumberInput(attrs={'placeholder': 'متوسط حل‌نشده'}),
    )
    hard = forms.IntegerField(
        min_value=0,
        required=False,
        label='H',
        widget=forms.NumberInput(attrs={'placeholder': 'سخت حل‌نشده'}),
    )
    sum_amount = forms.Field(
        required=False,
        widget=widgets.SumWidget(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['sum_amount'].widget.target_inputs = [
            {'weight': 1, 'name': 'amount'},
            {'weight': transaction.get_easy_price(), 'name': 'easy'},
            {'weight': transaction.get_medium_price(), 'name': 'medium'},
            {'weight': transaction.get_hard_price(), 'name': 'hard'},
            {'weight': transaction.get_solved_easy_price(), 'name': 'solved_easy'},
            {'weight': transaction.get_solved_medium_price(), 'name': 'solved_medium'},
            {'weight': transaction.get_solved_hard_price(), 'name': 'solved_hard'},
        ]

    def clean(self):
        super().clean()

        team_number = self.cleaned_data['team_number']
        try:
            team = models.Team.objects.get(team_number=team_number)
        except models.Team.DoesNotExist:
            raise ValidationError({'team_number': f'team number {team_number} does not exist'})

        if not competition.is_near_end():
            if self.cleaned_data.get('easy'):
                raise ValidationError({'easy': f'cannot buy unsolved problems now'})
            if self.cleaned_data.get('medium'):
                raise ValidationError({'medium': f'cannot buy unsolved problems now'})
            if self.cleaned_data.get('hard'):
                raise ValidationError({'hard': f'cannot buy unsolved problems now'})

        amount = transaction.calculate_amount(
            amount=self.cleaned_data.get('amount') or 0,
            easy=self.cleaned_data.get('easy') or 0,
            medium=self.cleaned_data.get('medium') or 0,
            hard=self.cleaned_data.get('hard') or 0,
            solved_easy=self.cleaned_data.get('solved_easy') or 0,
            solved_medium=self.cleaned_data.get('solved_medium') or 0,
            solved_hard=self.cleaned_data.get('solved_hard') or 0,
        )

        if amount == 0:
            raise ValidationError({
                '__all__': 'cannot record a transaction with zero amount',
                'amount': '',
                'easy': '',
                'medium': '',
                'hard': '',
                'solved_easy': '',
                'solved_medium': '',
                'solved_hard': '',
            })

        if amount < 0:
            if team.balance + amount < -transaction.calculate_max_loan(team.balance):
                raise ValidationError({
                    '__all__': 'insufficient funds',
                    'amount': '',
                    'easy': '',
                    'medium': '',
                    'hard': '',
                    'solved_easy': '',
                    'solved_medium': '',
                    'solved_hard': '',
                })


class StartCompetitionForm(forms.Form):
    teams_count = forms.IntegerField(required=True, min_value=1)


class FinishCompetitionForm(forms.Form):
    pass


class TransactionFilterForm(forms.Form):
    team_number = forms.IntegerField(required=False)
    recorded_by = forms.ModelChoiceField(queryset=User.objects.all(), required=False)
