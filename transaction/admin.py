import csv

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.urls import path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from transaction import models
from transaction.forms import UserForm
from transaction.forms import UserInlineForm
from transaction.models import Team

User = get_user_model()

admin.site.unregister(Group)

admin.site.register(models.Team)

admin.site.register(models.Transaction)


class UserAdmin(admin.ModelAdmin):
    fields = ["username", "custom_password", "is_superuser", "competition"]
    form = UserForm


admin.site.register(User, UserAdmin)


class UserInline(admin.TabularInline):
    model = User
    form = UserInlineForm
    fields = ["existing_user", "username", "custom_password"]
    extra = 1
    can_delete = False


class CompetitionAdmin(admin.ModelAdmin):
    inlines = [UserInline]
    change_form_template = "admin/competition_change_form.html"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        Team.objects.bulk_create(
            [
                Team(team_number=team_number, balance=0, competition=obj)
                for team_number in range(1, obj.teams_count + 1)
            ],
            ignore_conflicts=True,
        )
        Team.all_objects.filter(competition=obj, team_number__lte=obj.teams_count).update(deactivated=False)
        Team.objects.filter(competition=obj, team_number__gt=obj.teams_count).update(deactivated=True)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:object_id>/teams/csv/",
                self.admin_site.admin_view(self.download_csv),
                name="competition_teams_csv",
            ),
            path(
                "<int:object_id>/teams/pdf/",
                self.admin_site.admin_view(self.download_pdf),
                name="competition_teams_pdf",
            ),
        ]
        return custom_urls + urls

    def download_csv(self, request, object_id):
        obj = self.get_object(request, object_id)

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{obj.slug}.csv"'

        writer = csv.writer(response)

        writer.writerow(["Rank", "Team Number", "Balance"])
        for i, team in enumerate(obj.team_set.order_by("-balance")):
            writer.writerow([i + 1, team.team_number, team.balance])

        return response

    def download_pdf(self, request, object_id):
        obj = self.get_object(request, object_id)

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{obj.slug}.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4

        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, height - 50, f"Competition: {obj.slug}")

        p.setFont("Helvetica", 12)
        y = height - 100

        p.drawString(100, y, "Rank | Team Number | Balance")
        y -= 20

        for i, team in enumerate(obj.team_set.order_by("-balance")):
            p.drawString(100, y, f"{i + 1} | {team.team_number} | {team.balance}")
            y -= 20

        p.showPage()
        p.save()
        return response


admin.site.register(models.Competition, CompetitionAdmin)

admin.site.site_header = settings.ADMIN_SITE_HEADER
admin.site.site_title = settings.ADMIN_SITE_TITLE
admin.site.index_title = settings.ADMIN_INDEX_TITLE
