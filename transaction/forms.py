from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy

from transaction.models import Competition
from transaction.models import Team
from transaction.widgets import RequestWidget
from transaction.widgets import SumWidget

User = get_user_model()


class TransactionForm(forms.Form):
    team_number = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={"placeholder": "شماره تیم"}),
    )
    team_balance = forms.Field(
        required=False,
        widget=RequestWidget(target_input="team_number", endpoint=reverse_lazy("api-teams-get_balance_by_number")),
    )
    amount = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={"placeholder": "مقدار"}),
    )
    solved_easy = forms.IntegerField(
        min_value=0,
        required=False,
        label="SE",
        widget=forms.NumberInput(attrs={"placeholder": "ساده حل‌شده"}),
    )
    solved_medium = forms.IntegerField(
        min_value=0,
        required=False,
        label="SM",
        widget=forms.NumberInput(attrs={"placeholder": "متوسط حل‌شده"}),
    )
    solved_hard = forms.IntegerField(
        min_value=0,
        required=False,
        label="SH",
        widget=forms.NumberInput(attrs={"placeholder": "سخت حل‌شده"}),
    )
    easy = forms.IntegerField(
        min_value=0,
        required=False,
        label="E",
        widget=forms.NumberInput(attrs={"placeholder": "ساده حل‌نشده"}),
    )
    medium = forms.IntegerField(
        min_value=0,
        required=False,
        label="M",
        widget=forms.NumberInput(attrs={"placeholder": "متوسط حل‌نشده"}),
    )
    hard = forms.IntegerField(
        min_value=0,
        required=False,
        label="H",
        widget=forms.NumberInput(attrs={"placeholder": "سخت حل‌نشده"}),
    )
    sum_amount = forms.Field(
        required=False,
        widget=SumWidget(),
    )

    def clean(self):
        super().clean()

        team_number = self.cleaned_data["team_number"]

        try:
            team = Team.objects.get(team_number=team_number)
        except Team.DoesNotExist:
            raise ValidationError({"team_number": f"team number {team_number} does not exist"})

        if not team.competition.is_near_end():
            if self.cleaned_data.get("easy"):
                raise ValidationError({"easy": "cannot buy unsolved problems now"})
            if self.cleaned_data.get("medium"):
                raise ValidationError({"medium": "cannot buy unsolved problems now"})
            if self.cleaned_data.get("hard"):
                raise ValidationError({"hard": "cannot buy unsolved problems now"})

        amount = team.competition.calculate_amount(
            amount=self.cleaned_data.get("amount") or 0,
            easy=self.cleaned_data.get("easy") or 0,
            medium=self.cleaned_data.get("medium") or 0,
            hard=self.cleaned_data.get("hard") or 0,
            solved_easy=self.cleaned_data.get("solved_easy") or 0,
            solved_medium=self.cleaned_data.get("solved_medium") or 0,
            solved_hard=self.cleaned_data.get("solved_hard") or 0,
        )

        if amount == 0:
            raise ValidationError(
                {
                    "__all__": "cannot record a transaction with zero amount",
                    "amount": "",
                    "easy": "",
                    "medium": "",
                    "hard": "",
                    "solved_easy": "",
                    "solved_medium": "",
                    "solved_hard": "",
                }
            )

        if amount < 0:
            if team.balance + amount < -team.competition.calculate_max_loan(team.balance):
                raise ValidationError(
                    {
                        "__all__": "insufficient funds",
                        "amount": "",
                        "easy": "",
                        "medium": "",
                        "hard": "",
                        "solved_easy": "",
                        "solved_medium": "",
                        "solved_hard": "",
                    }
                )


class TransactionFilterForm(forms.Form):
    team_number = forms.IntegerField(required=False)
    recorded_by = forms.ModelChoiceField(queryset=User.objects.all(), required=False)


class CompetitionSelectionNavbarForm(forms.Form):
    competition = forms.ModelChoiceField(
        queryset=Competition.objects.all(),
        label="",
        widget=forms.Select(attrs={"class": "js-ab-submit ab-competition-selection"}),
        empty_label="no competition",
        required=False,
    )


class UserForm(forms.ModelForm):
    custom_password = forms.CharField(
        required=False, label="Password", widget=forms.PasswordInput(attrs={"placeholder": "current password"})
    )

    def save(self, commit=True):
        if self.cleaned_data["custom_password"]:
            self.instance.set_password(self.cleaned_data["custom_password"])

        self.instance.is_staff = self.cleaned_data["is_superuser"]

        return super().save(commit=commit)


class UserInlineForm(forms.ModelForm):
    existing_user = forms.ModelChoiceField(
        queryset=User.objects.all(), label="Select User", empty_label="New User", required=False
    )

    custom_password = forms.CharField(
        required=False, label="Password", widget=forms.PasswordInput(attrs={"placeholder": "current password"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["existing_user"].initial = self.instance

    class Media:
        js = ("assets/js/admin/user_inline.js",)

    def clean(self):
        cleaned_data = super().clean()

        if existing_user := cleaned_data.get("existing_user"):
            competition = self.instance.competition
            self.instance = existing_user
            self.instance.competition = competition

        return cleaned_data

    def save(self, commit=True):
        if self.cleaned_data["custom_password"]:
            self.instance.set_password(self.cleaned_data["custom_password"])

        return super().save(commit=commit)
