from rest_framework.metadata import SimpleMetadata

from unicef_restlib.metadata import ModelChoiceFieldMixin


class ImageFileTypeMetadata(ModelChoiceFieldMixin, SimpleMetadata):
    pass
