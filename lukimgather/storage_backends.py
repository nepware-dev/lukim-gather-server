import os
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.storage import FileSystemStorage


class CKEditorStorage(FileSystemStorage):
    location = os.path.join(settings.MEDIA_ROOT, "django_ckeditor_5")

    def get_base_url(self):
        request = None
        domain = get_current_site(request).domain
        return urljoin(f"{domain}", urljoin(settings.MEDIA_URL, "django_ckeditor_5/"))

    @property
    def base_url(self):
        return self.get_base_url()
