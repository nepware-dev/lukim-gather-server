from modeltranslation import translator

from survey.models import ProtectedAreaCategory


@translator.register(ProtectedAreaCategory)
class AreaCategoryTranslationOptions(translator.TranslationOptions):
    fields = ("title",)
