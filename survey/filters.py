import django_filters

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


class SurveyFilter(django_filters.FilterSet):
    class Meta:
        model = Survey
        fields = {
            "id": ["exact"],
            "title": ["exact", "contains"],
        }
