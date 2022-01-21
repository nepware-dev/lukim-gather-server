from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

from .schema import schema

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "graphql",
        csrf_exempt(
            GraphQLView.as_view(graphiql=not settings.IS_SERVER_SECURE, schema=schema)
        ),
        name="api",
    ),
]
