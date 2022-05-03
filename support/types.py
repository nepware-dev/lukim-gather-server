from graphene_django.types import DjangoObjectType

from support.models import LegalDocument


class LegalDocumentType(DjangoObjectType):
    class Meta:
        model = LegalDocument
        description = "Type defination for a legal document"
        fields = "__all__"
