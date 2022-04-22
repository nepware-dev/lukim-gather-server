from modeltranslation import translator

from survey.models import Option, ProtectedAreaCategory, Question, QuestionGroup


@translator.register(ProtectedAreaCategory)
class AreaCategoryTranslationOptions(translator.TranslationOptions):
    fields = ("title",)


@translator.register(QuestionGroup)
class QuestionGroupTranslationOptions(translator.TranslationOptions):
    fields = ("title",)


@translator.register(Question)
class QuestionTranslationOptions(translator.TranslationOptions):
    fields = ("title", "description", "hints")


@translator.register(Option)
class OptionTranslationOptions(translator.TranslationOptions):
    fields = ("title",)
