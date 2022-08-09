import django_filters

from .models import ProtectedArea, Region


class RegionFilter(django_filters.FilterSet):
    class Meta:
        model = Region
        fields = {
            "name": ["icontains"],
            "parent": ["exact"],
            "level": ["exact"],
        }


class ProtectedAreaFilter(django_filters.FilterSet):
    class Meta:
        model = ProtectedArea
        fields = {
            "name": ["icontains"],
            "parent": ["exact"],
            "level": ["exact"],
        }
