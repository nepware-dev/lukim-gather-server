import django_filters

from .models import (
    Category,
    FrequentlyAskedQuestion,
    LegalDocument,
    LegalDocumentTypeChoice,
    Resource,
    Tutorial,
)


class CategoryFilter(django_filters.FilterSet):
    class Meta:
        model = Category
        fields = {
            "title": ["exact", "icontains"],
            "parent": ["exact"],
            "level": ["exact"],
        }


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
            "title": ["contains"],
            "resource_type": ["exact"],
            "tags": ["exact"],
        }


class FAQFilter(django_filters.FilterSet):
    class Meta:
        model = FrequentlyAskedQuestion
        fields = {
            "question": ["icontains"],
            "answer": ["icontains"],
            "category": ["exact"],
        }


class TutorialFilter(django_filters.FilterSet):
    class Meta:
        model = Tutorial
        fields = {
            "question": ["icontains"],
            "answer": ["icontains"],
            "category": ["exact"],
        }
