import graphene
from graphene_django_extras import DjangoFilterPaginateListField

from .filters import LegalDocumentFilter, ResourceFilter
from .mutations import FeedbackMutation
from .types import (
    FrequentlyAskedQuestionType,
    LegalDocumentType,
    ResourceTagType,
    ResourceType,
)


class SupportQueries(graphene.ObjectType):
    legal_document = DjangoFilterPaginateListField(
        LegalDocumentType,
        description="Return the legal documents",
        filterset_class=LegalDocumentFilter,
    )
    frequently_asked_question = DjangoFilterPaginateListField(
        FrequentlyAskedQuestionType,
        description="Return the frequently asked questions",
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
