from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from graphene_file_upload.django import FileUploadGraphQLView

from user.views import UserInfoView

from .schema import schema

urlpatterns = i18n_patterns(
    path("admin/", admin.site.urls), prefix_default_language=False
)

urlpatterns += [
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
    path("oauth/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    path("api/user", UserInfoView.as_view()),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
