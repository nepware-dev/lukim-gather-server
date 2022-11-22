from graphene_django.types import DjangoObjectType

from support.models import (
    AccountDeletionRequest,
    Category,
    FrequentlyAskedQuestion,
    LegalDocument,
    Resource,
    ResourceTag,
    Tutorial,
)


class AccountDeletionRequestType(DjangoObjectType):
    class Meta:
        model = AccountDeletionRequest
        description = "Type defination for account deletion request"
        fields = ("reason",)


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        description = "Type defination for a category"
        fields = "__all__"


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

    def resolve_attachment(self, info):
        if self.attachment and self.attachment.url:
            return info.context.build_absolute_uri(self.attachment.url)
        else:
            return None


class FrequentlyAskedQuestionType(DjangoObjectType):
    class Meta:
        model = FrequentlyAskedQuestion
        description = "Type defination for a frequently asked question"
        fields = "__all__"


class TutorialType(DjangoObjectType):
    class Meta:
        model = Tutorial
        description = "Type defination for a tutorials"
        fields = "__all__"
