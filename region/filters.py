import django_filters

from .models import Region


class RegionFilter(django_filters.FilterSet):
    class Meta:
        model = Region
        fields = {
            "name": ["icontains"],
            "parent": ["exact"],
            "level": ["exact"],
        }
