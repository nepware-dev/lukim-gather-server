from modeltranslation import translator

from support.models import FrequentlyAskedQuestion, LegalDocument, Resource


@translator.register(LegalDocument)
class LegalDocumentTranslationOptions(translator.TranslationOptions):
    fields = ("description",)


@translator.register(FrequentlyAskedQuestion)
class FrequentlyAskedQuestionTranslationOptions(translator.TranslationOptions):
    fields = ("question", "answer")


@translator.register(Resource)
class ResourceTranslationOptions(translator.TranslationOptions):
    fields = ("title", "description")
