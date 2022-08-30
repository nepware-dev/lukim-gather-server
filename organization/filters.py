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
            "members__id": ["exact"],
        }

    @property
    def qs(self):
        parent = super(OrganizationFilter, self).qs
        member_id = self.data.get("members__id", None)
        if member_id:
            if self.request.user.is_anonymous or member_id != int(self.request.user.id):
                return parent.none()
        return parent
