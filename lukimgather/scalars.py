from pathlib import Path

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
            raise GraphQLError(
                "Upload a valid image. The file you uploaded was either not an image or a corrupted image."
            )
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


class UploadAudio(graphene.Scalar):
    @staticmethod
    def validate_audio(upload):
        audio_type_dict = {
            "aac": "audio/aac",
            "midi": "audio/midi",
            "mp3": "audio/mpeg",
            "m4a": "audio/mp4",
            "mp4": "audio/mp4",
            "ogg": "audio/ogg",
            "flac": "audio/x-flac",
            "wav": "audio/x-wav",
            "amr": "audio/amr",
            "aiff": "audio/x-aiff",
        }

        extension = Path(upload.name).suffix[1:].lower()
        if extension not in audio_type_dict.keys():
            raise GraphQLError(
                "Upload a valid audio. The file you uploaded was either not an audio or a corrupted audio file."
            )
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
        return UploadAudio.validate_audio(value)
