from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _
from django_filters import FilterSet
from django_filters.filters import ChoiceFilter

from .models import Project


class TabChoice(TextChoices):
    MY_PROJECT = "my_project", _("My Project")


class ProjectFilter(FilterSet):
    tab = ChoiceFilter(label="tab", method="get_tab", choices=TabChoice.choices)

    class Meta:
        model = Project
        fields = {
            "id": ["exact"],
            "title": ["exact"],
            "organization": ["exact"],
        }

    def get_tab(self, queryset, name, value):
        user = self.request.user
        my_projects = queryset.filter(users=user).distinct()
        if value == TabChoice.MY_PROJECT:
            return my_projects
