from unicef_restlib import utils


def test_get_attribute_smart_instance_none():
    assert utils.get_attribute_smart(None, "instances.id") is None


def test_get_attribute_smart_no_attrs():
    assert utils.get_attribute_smart(1, "") == 1


def test_get_attribute_smart():
    assert utils.get_attribute_smart({"instances": [{"id": 1}, {"id": 2}, {"id": 3}]}, "instances.id") == [1, 2, 3]
