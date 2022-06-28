from graphene_django.types import DjangoObjectType

from support.models import FrequentlyAskedQuestion, LegalDocument, Resource, ResourceTag


class LegalDocumentType(DjangoObjectType):
    class Meta:
        model = LegalDocument
        description = "Type defination for a legal document"
        fields = "__all__"


class ResourceTagType(DjangoObjectType):
    class Meta:
        model = ResourceTag
        description = "Type defination for a resource tag"
        fields = "__all__"


class ResourceType(DjangoObjectType):
    class Meta:
        model = Resource
        description = "Type defination for a resource"
        fields = "__all__"


class FrequentlyAskedQuestionType(DjangoObjectType):
    class Meta:
        model = FrequentlyAskedQuestion
        description = "Type defination for a frequently asked question"
        fields = "__all__"
