import django_filters

from .models import LegalDocument, LegalDocumentTypeChoice


class LegalDocumentFilter(django_filters.FilterSet):
    document_type = django_filters.ChoiceFilter(choices=LegalDocumentTypeChoice.choices)

    class Meta:
        model = LegalDocument
        fields = [
            "id",
            "document_type",
        ]
