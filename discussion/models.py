from ckeditor.fields import RichTextField
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from lukimgather.models import TimeStampedModel


class Comment(TimeStampedModel, MPTTModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="comments",
    )
    description = RichTextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(_("object id"), max_length=255, null=True, blank=True)
    content_object = GenericForeignKey()
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"Comment: #{self.pk}"


class LikeComment(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="liked_comments",
    )
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "comment"], name="Unique user and comment field"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.comment}"
