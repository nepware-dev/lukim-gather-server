from ckeditor.fields import RichTextField
from django.db import models
from django.template import Context, Template
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from ordered_model.models import OrderedModel

from lukimgather.models import TimeStampedModel, UserStampedModel


class LegalDocumentTypeChoice(models.TextChoices):
    ABOUT = "about", _("About")
    TERMS_AND_CONDITIONS = "terms-and-conditions", _("Terms And Conditions")
    PRIVACY_POLICY = "privacy-policy", _("Privacy Policy")
    COOKIE_POLICY = "cookie-policy", _("Cookie Policy")


class LegalDocument(UserStampedModel, TimeStampedModel):
    document_type = models.CharField(
        _("document type"),
        max_length=20,
        choices=LegalDocumentTypeChoice.choices,
        unique=True,
    )
    description = RichTextField(_("description"))

    def __str__(self):
        return self.document_type

    def save(self, *args, **kwargs):
        if self.pk:
            cls = self.__class__
            old = cls.objects.get(pk=self.pk)
            changed_fields = []
            for field in cls._meta.get_fields():
                field_name = field.name
                try:
                    old_val = getattr(old, field_name)
                    new_val = getattr(self, field_name)
                    if hasattr(field, "is_custom_lower_field"):
                        if field.is_custom_lower_field():
                            new_val = new_val.lower()
                    if old_val != new_val:
                        changed_fields.append(field_name)
                except Exception:
                    pass
            kwargs["update_fields"] = changed_fields
        super().save(*args, **kwargs)


class Feedback(UserStampedModel, TimeStampedModel):
    title = models.CharField(_("title"), max_length=255)
    description = RichTextField(_("description"))

    def __str__(self):
        return self.title


class Category(MPTTModel):
    title = models.TextField(_("title"), max_length=255)
    parent = TreeForeignKey(
        "self", null=True, blank=True, related_name="children", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = _("categories")


class FrequentlyAskedQuestion(UserStampedModel, TimeStampedModel, OrderedModel):
    question = models.TextField(_("question"))
    answer = RichTextField(_("answer"))
    category = models.ForeignKey(
        "Category",
        null=True,
        related_name="frequentlyaskedquestions",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.question

    class Meta(OrderedModel.Meta):
        pass


class Tutorial(UserStampedModel, TimeStampedModel, OrderedModel):
    question = models.TextField(_("question"))
    answer = RichTextField(_("answer"))
    category = models.ForeignKey(
        "Category", null=True, related_name="tutorials", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.question

    class Meta(OrderedModel.Meta):
        pass


class ResourceTag(UserStampedModel, TimeStampedModel, OrderedModel):
    title = models.CharField(_("title"), max_length=50)

    def __str__(self):
        return self.title

    class Meta(OrderedModel.Meta):
        pass


class Resource(UserStampedModel, TimeStampedModel, OrderedModel):
    class ResourceTypeChoices(models.TextChoices):
        ATTACHMENT = "attachment", _("Attachment")
        VIDEO = "video", _("Video")

    title = models.TextField(_("title"), max_length=255)
    description = RichTextField(_("description"))
    resource_type = models.CharField(
        _("resource type"), max_length=10, choices=ResourceTypeChoices.choices
    )
    video_url = models.URLField(_("video url"), null=True, blank=True, default=None)
    attachment = models.FileField(_("attachment"), null=True, blank=True, default=None)
    tags = models.ManyToManyField(
        "ResourceTag", related_name="resources", verbose_name=_("resource tags")
    )

    def __str__(self):
        return self.title

    class Meta(OrderedModel.Meta):
        pass


class EmailTemplate(models.Model):
    identifier = models.CharField(_("identifier"), max_length=50, unique=True)
    subject = models.CharField(_("subject"), max_length=255)
    html_message = RichTextField(_("html message"))
    text_message = models.TextField(_("text message"))

    def __str__(self):
        return self.identifier

    def get_email_contents(self, context):
        html_template = Template(self.html_message)
        text_template = Template(self.text_message)
        html_message = html_template.render(Context(context))
        text_message = text_template.render(Context(context))
        return self.subject, html_message, text_message
