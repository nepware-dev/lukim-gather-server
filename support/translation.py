from modeltranslation import translator

from support.models import LegalDocument


@translator.register(LegalDocument)
class LegalDocumentTranslationOptions(translator.TranslationOptions):
    fields = ("description",)
