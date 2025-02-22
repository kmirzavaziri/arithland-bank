from django.conf import settings

from transaction.forms import CompetitionSelectionNavbarForm


def add_base_context(request):
    user_context = {
        "is_superuser": request.user.is_superuser,
    }

    menu_context = settings.MENU_COMMON

    if request.user.is_superuser:
        menu_context = settings.MENU_ADMIN

    competition_context = {}

    if request.user.is_authenticated and request.user.competition_id:
        competition = request.user.competition

        competition_context["current_time"] = competition.get_current_time()
        competition_context["slug"] = competition.slug
        competition_context["is_before"] = competition.get_current_time() < 0
        competition_context["is_after"] = competition.get_current_time() > competition.competition_length_sec

    forms_context = {}

    if request.user.is_superuser:
        forms_context["competition_selection"] = CompetitionSelectionNavbarForm(
            data={
                "competition": request.user.competition,
            }
        )

    return {
        "base": {
            "user": user_context,
            "menu": menu_context,
            "competition": competition_context,
            "forms": forms_context,
        }
    }
