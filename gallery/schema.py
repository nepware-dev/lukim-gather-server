import graphene

from gallery.mutations import MediaUploadMutation


class UploadFileMutation(graphene.ObjectType):
    upload_media = MediaUploadMutation.Field()
