from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response


@api_view(["GET"])
@renderer_classes([JSONRenderer])
def generate_204(response, format=None):
    return Response(None, status=status.HTTP_204_NO_CONTENT)
