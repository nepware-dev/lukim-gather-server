import graphene
from graphene_django.types import DjangoObjectType
from sorl.thumbnail import get_thumbnail

from gallery.models import Gallery


class GalleryMediaType(graphene.ObjectType):
    og = graphene.String()
    sm = graphene.String()
    lg = graphene.String()


class GalleryType(DjangoObjectType):
    media = graphene.Field(GalleryMediaType)

    class Meta:
        model = Gallery
        exclude = ("type",)

    def resolve_media(self, info):
        if not self.media or not self.media.url:
            return None

        if self.type == "image":
            img_quality_sm = get_thumbnail(
                self.media, "400x400", crop="center", quality=60
            )
            img_quality_lg = get_thumbnail(
                self.media, "700x700", crop="center", quality=99
            )
            return GalleryMediaType(
                og=info.context.build_absolute_uri(self.media.url),
                sm=info.context.build_absolute_uri(img_quality_sm.url),
                lg=info.context.build_absolute_uri(img_quality_lg.url),
            )

        return GalleryMediaType(og=info.context.build_absolute_uri(self.media.url))
