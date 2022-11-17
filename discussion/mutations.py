import graphene
from graphene.types.generic import GenericScalar
from graphene_django.rest_framework.mutation import SerializerMutation
from graphql_jwt.decorators import login_required

from discussion.models import LikeComment

from .serializers import CommentSerializer, LikeCommentSerializer


class CommentMutation(SerializerMutation):
    class Meta:
        serializer_class = CommentSerializer

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        input["user"] = info.context.user.id
        return super().mutate_and_get_payload(root, info, **input)


class LikeCommentMutation(SerializerMutation):
    class Meta:
        serializer_class = LikeCommentSerializer

    @classmethod
    @login_required
    def perform_mutate(cls, serializer, info):
        serializer.save(user=info.context.user)
        return super().perform_mutate(serializer, info)


class DislikeCommentMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    errors = GenericScalar()

    @classmethod
    @login_required
    def mutate(cls, root, info, id):
        try:
            LikeComment.objects.filter(user=info.context.user, comment__pk=id).delete()
        except Exception as e:
            return cls(ok=False, errors=str(e))
        return cls(ok=True, errors=None)
