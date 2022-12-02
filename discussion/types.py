import graphene
from graphene_django.types import DjangoObjectType

from discussion.models import Comment, LikeComment


class CommentType(DjangoObjectType):
    total_likes = graphene.Int()
    has_liked = graphene.Boolean()

    class Meta:
        model = Comment
        fields = "__all__"

    def resolve_total_likes(self, info):
        return self.likes.count()

    def resolve_has_liked(self, info):
        user = info.context.user
        if user:
            return self.likes.filter(user=user).exists()
        return False


class LikeCommentType(DjangoObjectType):
    class Meta:
        model = LikeComment
        fields = "__all__"
