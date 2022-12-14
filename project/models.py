from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from ordered_model.models import OrderedModel

from lukimgather.models import TimeStampedModel, UserStampedModel


class Project(TimeStampedModel, UserStampedModel, OrderedModel):
    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"))
    organization = models.ForeignKey(
        "organization.Organization",
        on_delete=models.CASCADE,
        related_name="projects",
        null=True,
        blank=True,
        default=None,
        verbose_name=_("organization"),
    )
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="projects",
        through="ProjectUser",
        through_fields=("project", "user"),
        verbose_name=_("users"),
    )

    class Meta(OrderedModel.Meta):
        pass

    def __str__(self):
        return self.title


class ProjectUser(TimeStampedModel, UserStampedModel):
    project = models.ForeignKey(
        "Project", on_delete=models.CASCADE, verbose_name=_("project")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("user")
    )
    is_admin = models.BooleanField(default=False)
