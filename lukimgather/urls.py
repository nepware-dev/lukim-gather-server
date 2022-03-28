from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from graphene_file_upload.django import FileUploadGraphQLView

from .schema import schema

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "graphql",
        csrf_exempt(
            FileUploadGraphQLView.as_view(
                graphiql=not settings.IS_SERVER_SECURE, schema=schema
            )
        ),
        name="api",
    ),
    path("ckeditor/", include("ckeditor_uploader.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
