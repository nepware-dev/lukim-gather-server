import uuid

from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.gis.db.models import MultiPolygonField, PointField
from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from ordered_model.models import OrderedModel

from lukimgather.models import CodeModel, TimeStampedModel, UserStampedModel


class Form(CodeModel, UserStampedModel, TimeStampedModel, OrderedModel):
    title = models.CharField(_("title"), max_length=255)
    description = RichTextUploadingField(
        _("description"), blank=True, null=True, default=None
    )

    def __str__(self):
        return self.code + "-" + self.title

    class Meta(OrderedModel.Meta):
        verbose_name = _("Form")
        verbose_name_plural = _("Forms")


class QuestionGroup(CodeModel, UserStampedModel, TimeStampedModel, OrderedModel):
    title = models.CharField(_("title"), max_length=255)
    skip_logic = models.TextField(_("skip logic"), null=True, blank=True, default=None)
    form = models.ForeignKey(
        "Form",
        on_delete=models.CASCADE,
        related_name="question_group",
        null=True,
        blank=True,
        default=None,
    )

    def __str__(self):
        return self.code + "-" + self.title

    class Meta(OrderedModel.Meta):
        verbose_name = _("Question group")
        verbose_name_plural = _("Question groups")


class AnswerTypeChoices(models.TextChoices):
    BOOLEAN = "boolean", _("Boolean")
    DATE = "date", _("Date")
    DESCRIPTION = "description", _("Description")
    SINGLE_IMAGE = "single_image", _("Single Image")
    MULTIPLE_IMAGE = "multiple_image", _("Multiple Image")
    LOCATION = "location", _("Location")
    NUMBER = "number", _("Number")
    TEXT = "text", _("Text")
    SINGLE_OPTION = "single_option", _("Single Option")
    MULTIPLE_OPTION = "multiple_option", _("Multiple Option")


class Question(CodeModel, UserStampedModel, TimeStampedModel, OrderedModel):
    title = models.TextField(_("title"))
    description = RichTextUploadingField(
        _("description"), blank=True, null=True, default=None
    )
    hints = models.TextField(_("hints"), blank=True, null=True, default=None)
    answer_type = models.CharField(
        _("answer type"), max_length=15, choices=AnswerTypeChoices.choices
    )
    group = models.ForeignKey(
        "QuestionGroup",
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name=_("question group"),
    )
    is_required = models.BooleanField(_("required"), default=True)
    skip_logic = models.TextField(_("skip logic"), null=True, blank=True, default=None)

    def __str__(self):
        return self.code + "-" + self.title

    class Meta(OrderedModel.Meta):
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")


class Option(CodeModel, UserStampedModel, TimeStampedModel, OrderedModel):
    title = models.TextField(_("title"))
    question = models.ForeignKey(
        "Question",
        on_delete=models.CASCADE,
        related_name="options",
        verbose_name=_("question"),
    )

    def __str__(self):
        return self.code + "-" + self.title

    class Meta(OrderedModel.Meta):
        verbose_name = _("Option")
        verbose_name_plural = _("Options")


class Survey(UserStampedModel, TimeStampedModel, OrderedModel):
    title = models.CharField(_("title"), max_length=255)

    def __str__(self):
        return self.title

    class Meta(OrderedModel.Meta):
        verbose_name = _("Survey")
        verbose_name_plural = _("Surveys")


class SurveyAnswer(UserStampedModel, TimeStampedModel):
    question = models.ForeignKey(
        "Question",
        on_delete=models.CASCADE,
        verbose_name=_("question"),
    )
    survey = models.ForeignKey(
        "Survey",
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name=_("survey"),
    )
    answer = models.TextField(_("answer"), null=True, blank=True, default=None)
    answer_type = models.CharField(
        _("answer type"), max_length=15, choices=AnswerTypeChoices.choices
    )
    options = models.ManyToManyField("Option", blank=True, verbose_name=_("options"))

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["question", "survey"],
                name="unique_survey_question",
            ),
        ]


class ProtectedAreaCategory(MPTTModel, TimeStampedModel, UserStampedModel, CodeModel):
    title = models.CharField(_("Title"), max_length=255)
    description = models.TextField(
        _("Description"), null=True, blank=True, default=None
    )
    parent = TreeForeignKey(
        "self", blank=True, null=True, related_name="child", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.title

    class MPTTMeta:
        order_insertion_by = ["title"]

    class Meta:
        verbose_name = _("Protected area category")
        verbose_name_plural = _("Protected area categories")


class Status(models.TextChoices):
    APPROVED = "approved", _("Approved")
    REJECTED = "rejected", _("Rejected")
    PENDING = "pending", _("Pending")


class Improvement(models.TextChoices):
    INCREASING = "increasing", _("Increasing")
    SAME = "same", _("Same")
    DECREASING = "decreasing", _("Decreasing")


class HappeningSurvey(TimeStampedModel, UserStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        "ProtectedAreaCategory",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="happening_survey",
    )
    title = models.CharField(
        _("title"), max_length=255, null=True, blank=True, default=None
    )
    description = models.TextField(
        _("Description"), null=True, blank=True, default=None
    )
    sentiment = models.TextField(_("Sentiments"), blank=True, null=True, default=None)
    attachment = models.ManyToManyField(
        "gallery.Gallery", blank=True, verbose_name=_("Attachments")
    )
    location = PointField(_("Location"), null=True, blank=True, default=None)
    boundary = MultiPolygonField(
        _("Location Boundary"), null=True, blank=True, default=None
    )
    status = models.CharField(
        verbose_name=_("Happening Survey Answer Status"),
        max_length=11,
        default=Status.PENDING,
        choices=Status.choices,
    )
    improvement = models.CharField(
        verbose_name=_("Happening Survey Improvement Status"),
        max_length=11,
        null=True,
        blank=True,
        default=None,
        choices=Improvement.choices,
    )
    data_dump = models.JSONField(blank=True, default=dict)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Happening survey")
        verbose_name_plural = _("Happening surveys")
