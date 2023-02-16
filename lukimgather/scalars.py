import graphene
from graphql import GraphQLError
from PIL import Image


class UploadImage(graphene.Scalar):
    @staticmethod
    def validate_image(upload):
        try:
            image = Image.open(upload)
            image.verify()
        except:
            raise GraphQLError("Invalid image type.")
        return upload

    @staticmethod
    def serialize(upload):
        return upload.name

    @staticmethod
    def parse_literal(node):
        raise Exception("File upload literals are not supported.")

    @staticmethod
    def parse_value(value):
        if not value:
            return None
        return UploadImage.validate_image(value)
