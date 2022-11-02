import django_filters

from .models import Organization


class OrganizationFilter(django_filters.FilterSet):
    class Meta:
        model = Organization
        fields = {
            "id": ["exact"],
            "title": ["contains"],
            "acronym": ["contains"],
            "description": ["contains"],
            "email": ["contains"],
            "website": ["contains"],
            "address": ["contains"],
        }
