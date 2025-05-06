import json

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render

from transaction.forms import TransactionFilterForm
from transaction.forms import TransactionForm
from transaction.models import Team
from transaction.models import Transaction
from transaction.transaction import perform_transaction
from transaction.ui import FormUI
from transaction.ui import MessageUI

User = get_user_model()


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form_ctx = {
        "ui": FormUI(
            title="Login",
            submit_button=FormUI.SubmitButton(text="Login"),
        )
    }

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        form_ctx["form"] = form
        if form.is_valid():
            user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password"])
            if user is not None:
                login(request, user)
                return redirect("dashboard")
        else:
            return render(request, "form.html", form_ctx)
    else:
        form_ctx["form"] = AuthenticationForm()
        return render(request, "form.html", form_ctx)


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")

    return redirect("dashboard")


def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.competition_id:
        return render(
            request,
            "message.html",
            {
                "ui": MessageUI(
                    "No Competition", "No competition is associated to your account. Ask admin to associate."
                ),
            },
        )

    form_ui = FormUI(
        title="New Transaction",
        submit_button=FormUI.SubmitButton(text="Submit"),
    )

    recent_transactions = Transaction.objects.filter(recorded_by=request.user).order_by("-id")[:4]

    if request.method == "POST":
        form = TransactionForm(request.POST, request=request)
        if form.is_valid():
            # TODO prompt when doing loan
            perform_transaction(
                user=request.user,
                team_number=form.cleaned_data["team_number"],
                amount=form.cleaned_data.get("amount") or 0,
                easy=form.cleaned_data.get("easy") or 0,
                medium=form.cleaned_data.get("medium") or 0,
                hard=form.cleaned_data.get("hard") or 0,
                solved_easy=form.cleaned_data.get("solved_easy") or 0,
                solved_medium=form.cleaned_data.get("solved_medium") or 0,
                solved_hard=form.cleaned_data.get("solved_hard") or 0,
            )
            return render(
                request,
                "dashboard.html",
                {
                    "form": TransactionForm(request=request),
                    "ui": form_ui,
                    "recent_transactions": recent_transactions,
                },
            )

        return render(
            request,
            "dashboard.html",
            {
                "form": form,
                "ui": form_ui,
                "recent_transactions": recent_transactions,
            },
        )

    return render(
        request,
        "dashboard.html",
        {
            "form": TransactionForm(request=request),
            "ui": form_ui,
            "recent_transactions": recent_transactions,
        },
    )


def teams_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if not request.user.competition_id:
        return redirect("dashboard")

    return render(
        request,
        "teams.html",
        {
            "teams": Team.objects.filter(competition_id=request.user.competition_id).order_by("-balance"),
        },
    )


def transactions_view(request):
    if not request.user.is_superuser:
        return redirect("login")

    form = TransactionFilterForm(request.GET)

    transactions = Transaction.objects.filter(~Q(amount=0), team__competition=request.user.competition)

    if form.is_valid():
        if "team_number" in form.cleaned_data and form.cleaned_data["team_number"]:
            transactions = transactions.filter(team__team_number=form.cleaned_data["team_number"])

        if "recorded_by" in form.cleaned_data and form.cleaned_data["recorded_by"]:
            transactions = transactions.filter(recorded_by=form.cleaned_data["recorded_by"])

    return render(
        request,
        "transactions.html",
        {
            "form": form,
            "transactions": transactions.order_by("-id"),
        },
    )


@staff_member_required
def get_user_details_api_view(request, user_id):
    user = User.objects.filter(id=user_id).first()
    if user:
        return JsonResponse({"username": user.username})
    return JsonResponse({})


def teams_get_balance_by_number_api_view(request):
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

    try:
        team = Team.objects.get(competition_id=request.user.competition_id, team_number=data["team_number"])
    except Team.DoesNotExist:
        return JsonResponse({"value": ""})

    if team.competition.is_near_end():
        return JsonResponse({"value": "confidential"})

    return JsonResponse(
        {
            "value": f"balance: {team.balance}, "
            f"credit: {team.balance + team.competition.calculate_max_loan(team.balance)}",
        }
    )


@staff_member_required
def set_user_competition_api_view(request):
    print("request.POST")
    print(request.POST.get("competition"))
    request.user.competition_id = request.POST.get("competition")
    request.user.save()

    return JsonResponse({})
