import pytest
from demo.sample.metadata import ImageFileTypeMetadata
from demo.sample.serializers import ImageFileTypeSerializer
from tests.factories import FileTypeFactory

pytestmark = pytest.mark.django_db


def test_model_choice_field_metadata():
    file_type = FileTypeFactory(code="image")
    file_type_wrong = FileTypeFactory(code="wrong")
    serializer = ImageFileTypeSerializer()
    metadata = ImageFileTypeMetadata().get_serializer_info(serializer)
    file_type_choices = [x['value'] for x in metadata['file_type']['choices']]
    assert file_type.pk in file_type_choices
    assert file_type_wrong.pk not in file_type_choices
