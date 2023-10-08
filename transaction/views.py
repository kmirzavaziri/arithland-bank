import json
from dataclasses import dataclass

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect

from . import forms, transaction, competition, models


@dataclass
class FormUi:
    title: str

    @dataclass
    class SubmitButton:
        text: str

    submit_button: SubmitButton


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form_ctx = {
        'ui': FormUi(
            title='Login',
            submit_button=FormUi.SubmitButton(text='Login'),
        )
    }

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        form_ctx['form'] = form
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('dashboard')
        else:
            return render(request, 'form.html', form_ctx)
    else:
        form_ctx['form'] = AuthenticationForm()
        return render(request, 'form.html', form_ctx)


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')

    return redirect('dashboard')


def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    form_ui = FormUi(
        title='New Transaction',
        submit_button=FormUi.SubmitButton(text='Submit'),
    )

    recent_transactions = (
        models.Transaction.objects
        .filter(recorded_by=request.user).order_by('-id')[:4]
    )

    if request.method == 'POST':
        form = forms.TransactionForm(request.POST)
        if form.is_valid():
            # TODO prompt when doing loan
            transaction.perform_transaction(
                user=request.user,
                team_number=form.cleaned_data['team_number'],
                amount=form.cleaned_data.get('amount') or 0,
                easy=form.cleaned_data.get('easy') or 0,
                medium=form.cleaned_data.get('medium') or 0,
                hard=form.cleaned_data.get('hard') or 0,
                solved_easy=form.cleaned_data.get('solved_easy') or 0,
                solved_medium=form.cleaned_data.get('solved_medium') or 0,
                solved_hard=form.cleaned_data.get('solved_hard') or 0,
            )
            return render(request, 'dashboard.html', {
                'form': forms.TransactionForm(),
                'ui': form_ui,
                'recent_transactions': recent_transactions,
            })

        return render(request, 'dashboard.html', {
            'form': form,
            'ui': form_ui,
            'recent_transactions': recent_transactions,
        })

    return render(request, 'dashboard.html', {
        'form': forms.TransactionForm(),
        'ui': form_ui,
        'recent_transactions': recent_transactions,
    })


def teams_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    return render(request, 'teams.html', {
        "teams": models.Team.objects.order_by("-balance"),
    })


def teams_get_balance_by_number_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"value": ""})

    if request.method != "POST":
        return JsonResponse({"value": ""})

    try:
        data = json.loads(request.body)
    except json.decoder.JSONDecodeError:
        return JsonResponse({"value": ""})

    if "team_number" not in data or not data["team_number"]:
        return JsonResponse({"value": ""})

    if competition.is_near_end():
        return JsonResponse({"value": "confidential"})

    try:
        team = models.Team.objects.get(team_number=data["team_number"])
    except models.Team.DoesNotExist:
        return JsonResponse({"value": ""})

    return JsonResponse({
        "value": f"balance: {team.balance}, credit: {team.balance + transaction.calculate_max_loan(team.balance)}",
    })


def transactions_view(request):
    if not request.user.is_superuser:
        return redirect('login')

    form = forms.TransactionFilterForm(request.GET)
    transactions = models.Transaction.objects.filter(~Q(amount=0))

    if form.is_valid():
        if "team_number" in form.cleaned_data and form.cleaned_data["team_number"]:
            transactions = transactions.filter(team__team_number=form.cleaned_data["team_number"])

        if "recorded_by" in form.cleaned_data and form.cleaned_data["recorded_by"]:
            transactions = transactions.filter(recorded_by=form.cleaned_data["recorded_by"])

    return render(request, 'transactions.html', {
        "form": form,
        "transactions": transactions.order_by('-id'),
    })


def manage_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.is_superuser:
        return redirect('home')

    start_competition_form = forms.StartCompetitionForm()
    finish_competition_form = forms.FinishCompetitionForm()

    if request.method == 'POST':
        if 'start_competition' in request.POST:
            start_competition_form = forms.StartCompetitionForm(request.POST)
            if start_competition_form.is_valid():
                competition.start(start_competition_form.cleaned_data['teams_count'])
        elif 'finish_competition' in request.POST:
            finish_competition_form = forms.FinishCompetitionForm(request.POST)
            if finish_competition_form.is_valid():
                competition.finish()

    return render(request, 'manage.html', {
        'start_form': start_competition_form,
        'finish_form': finish_competition_form,
    })

    # TODO download result csv
