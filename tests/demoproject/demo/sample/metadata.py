from rest_framework.metadata import SimpleMetadata

from unicef_restlib import metadata


class ImageFileTypeMetadata(metadata.ModelChoiceFieldMixin, SimpleMetadata):
    pass


class ReadOnlyChoiceMetadata(metadata.ReadOnlyFieldWithChoicesMixin, SimpleMetadata):
    pass


class CRUMetadata(metadata.CRUActionsMetadataMixin, SimpleMetadata):
    pass


class FSMMetadata(metadata.FSMTransitionActionMetadataMixin, SimpleMetadata):
    pass


class SeparateReadWriteMetadata(metadata.SeparatedReadWriteFieldMetadata, SimpleMetadata):
    pass
