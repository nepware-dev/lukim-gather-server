import graphene
from graphene.types.generic import GenericScalar
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from gallery.models import Gallery
from gallery.types import GalleryType


class MediaUploadMutation(graphene.Mutation):
    gallery = graphene.Field(GalleryType)

    class Arguments:
        title = graphene.String(description="Title", required=True)
        type = graphene.String(description="Media Type", required=True)
        media = Upload(required=False)

    errors = GenericScalar()
    result = graphene.Field(GalleryType)
    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, media=None, **kwargs):
        if media is not None:
            gallery = Gallery(
                media=media, title=kwargs.get("title"), type=kwargs.get("type")
            )
            gallery.save()
            return MediaUploadMutation(result=gallery, ok=True, errors=None)
        else:
            return GraphQLError("Image required !")
