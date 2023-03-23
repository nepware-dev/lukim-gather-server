import graphene
from graphene_django_extras import DjangoFilterPaginateListField

from .filters import CategoryFilter, LegalDocumentFilter, ResourceFilter
from .mutations import (
    AccountDeletionRequestMutation,
    ContactUsMutation,
    FeedbackMutation,
)
from .types import (
    CategoryType,
    FrequentlyAskedQuestionType,
    LegalDocumentType,
    ResourceTagType,
    ResourceType,
    TutorialType,
)


class SupportQueries(graphene.ObjectType):
    support_category = DjangoFilterPaginateListField(
        CategoryType,
        description="Return the categories",
        filterset_class=CategoryFilter,
    )
    legal_document = DjangoFilterPaginateListField(
        LegalDocumentType,
        description="Return the legal documents",
        filterset_class=LegalDocumentFilter,
    )
    frequently_asked_question = DjangoFilterPaginateListField(
        FrequentlyAskedQuestionType,
        description="Return the frequently asked questions",
    )
    tutorial = DjangoFilterPaginateListField(
        TutorialType,
        description="Return the tutorials",
    )
    resource_tag = DjangoFilterPaginateListField(
        ResourceTagType,
        description="Return the resource tags",
    )
    resource = DjangoFilterPaginateListField(
        ResourceType,
        description="Return the resources",
        filterset_class=ResourceFilter,
    )


class SupportMutations(graphene.ObjectType):
    create_feedback = FeedbackMutation.Field()
    delete_account = AccountDeletionRequestMutation.Field()
    contact_us = ContactUsMutation.Field()
