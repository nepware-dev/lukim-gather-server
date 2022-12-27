import django_filters
from django.db.models import Q

from .models import Grant, User


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


class UserFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="get_search", label="User")

    class Meta:
        model = User
        fields = {
            "id": ["exact"],
        }

    def get_search(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
            | Q(username__icontains=value)
        )

    @property
    def qs(self):
        parent = super(UserFilter, self).qs
        if self.request.user.is_anonymous:
            return parent.none()
        search_params = self.data.get("search")
        if search_params is not None and not len(search_params) > 2:
            return parent.none()
        return parent
