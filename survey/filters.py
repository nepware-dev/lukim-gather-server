import django_filters
from reversion.models import Version

from survey.models import HappeningSurvey, Survey


class HappeningSurveyFilter(django_filters.FilterSet):
    class Meta:
        model = HappeningSurvey
        fields = {
            "id": ["exact"],
            "title": ["exact", "contains"],
            "project__title": ["exact", "icontains"],
            "category__title": ["exact", "icontains"],
            "region__name": ["exact", "icontains"],
            "is_public": [
                "exact",
            ],
        }


class HappeningSurveyHistoryFilter(django_filters.FilterSet):
    class Meta:
        model = Version
        fields = {
            "id": ["exact"],
            "object_id": ["exact"],
            "object_repr": ["exact", "icontains"],
            "revision__comment": ["exact"],
        }


class SurveyFilter(django_filters.FilterSet):
    class Meta:
        model = Survey
        fields = {
            "id": ["exact"],
            "title": ["exact", "contains"],
        }

    @property
    def qs(self):
        parent = super(SurveyFilter, self).qs.order_by("-created_at")
        return parent
