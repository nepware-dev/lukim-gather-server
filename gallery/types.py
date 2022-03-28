from graphene_django.types import DjangoObjectType

from gallery.models import Gallery


class GalleryType(DjangoObjectType):
    class Meta:
        model = Gallery
        exclude = ("type",)
