import django_filters

from survey.models import HappeningSurvey


class HappeningSurveyFilter(django_filters.FilterSet):
    class Meta:
        model = HappeningSurvey
        fields = {
            "id": ["exact"],
            "title": ["exact", "contains"],
        }
