from modeltranslation.translator import translator, TranslationOptions
from geoprisma.models import Resource


class ResourceTranslationOptions(TranslationOptions):
    fields = ('display_name',)

translator.register(Resource, ResourceTranslationOptions)
