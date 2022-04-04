from graphene_django.types import DjangoObjectType

from gallery.models import Gallery


class GalleryType(DjangoObjectType):
    class Meta:
        model = Gallery
        exclude = ("type",)

    def resolve_media(self, info):
        if self.media and self.media.url:
            return info.context.build_absolute_uri(self.media.url)
        else:
            return None
