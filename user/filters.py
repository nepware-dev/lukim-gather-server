import django_filters

from .models import Grant


class GrantFilter(django_filters.FilterSet):
    class Meta:
        model = Grant
        fields = {
            "id": ["exact"],
            "title": ["exact", "contains"],
            "description": ["exact", "contains"],
            "user__id": [
                "exact",
            ],
            "user__username": [
                "exact",
                "contains",
            ],
            "user__email": [
                "exact",
                "contains",
            ],
            "user__first_name": [
                "exact",
                "contains",
            ],
            "user__last_name": [
                "exact",
                "contains",
            ],
        }
