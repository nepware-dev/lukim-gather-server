import graphene
from graphene_django_extras import DjangoFilterPaginateListField

from .filters import LegalDocumentFilter
from .mutations import FeedbackMutation
from .types import LegalDocumentType


class SupportQueries(graphene.ObjectType):
    legal_document = DjangoFilterPaginateListField(
        LegalDocumentType,
        description="Return the legal documents",
        filterset_class=LegalDocumentFilter,
    )


class SupportMutations(graphene.ObjectType):
    create_feedback = FeedbackMutation.Field()
