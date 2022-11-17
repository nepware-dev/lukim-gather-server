import graphene
from graphene_django_extras.fields import DjangoFilterPaginateListField

from discussion.types import CommentType, LikeCommentType

from .filters import CommentFilter, LikeCommentFilter
from .mutations import CommentMutation, DislikeCommentMutation, LikeCommentMutation


class DiscussionQueries(graphene.ObjectType):
    comments = DjangoFilterPaginateListField(
        CommentType,
        description="Return comments",
        filterset_class=CommentFilter,
    )
    likes = DjangoFilterPaginateListField(
        LikeCommentType,
        description="Return likes",
        filterset_class=LikeCommentFilter,
    )


class DiscussionMutations(graphene.ObjectType):
    create_comment = CommentMutation.Field()
    like_comment = LikeCommentMutation.Field()
    dislike_comment = DislikeCommentMutation.Field()
