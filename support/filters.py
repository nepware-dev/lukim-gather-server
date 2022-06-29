import django_filters

from .models import LegalDocument, LegalDocumentTypeChoice, Resource


class LegalDocumentFilter(django_filters.FilterSet):
    document_type = django_filters.ChoiceFilter(choices=LegalDocumentTypeChoice.choices)

    class Meta:
        model = LegalDocument
        fields = [
            "id",
            "document_type",
        ]


class ResourceFilter(django_filters.FilterSet):
    class Meta:
        model = Resource
        fields = {
            "resource_type": ["exact"],
            "tags": ["exact"],
        }
