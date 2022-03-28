import datetime

import graphene
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from graphene.types.generic import GenericScalar
from graphene_file_upload.scalars import Upload
from graphql.execution.base import ResolveInfo
from graphql_jwt.decorators import login_required

from gallery.models import Gallery
from gallery.types import GalleryType


class MediaUploadMutation(graphene.Mutation):
    class Arguments:
        title = graphene.String(description="Title", required=True)
        type = graphene.String(description="Media Type", required=True)
        media = Upload(required=False)

    errors = GenericScalar()
    result = graphene.Field(GalleryType)
    ok = graphene.Boolean()

    @login_required
    def mutate(self, info: ResolveInfo, media=None, **data):
        date = datetime.date.today()
        upload_to = f"/attachments/{date:%Y}/{date:%m}/{date:%d}/"
        fs = FileSystemStorage(location=settings.MEDIA_ROOT + upload_to)
        file = fs.save(media, media)
        gallery = Gallery.objects.create(
            title=data.get("title"), media=upload_to + file
        )
        return MediaUploadMutation(result=gallery, ok=True, errors=None)
