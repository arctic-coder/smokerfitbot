# tests/test_form_helpers.py
from handlers.form import _to_list


def test_to_list_none():
    assert _to_list(None) == []


def test_to_list_empty_string():
    assert _to_list("") == []
    assert _to_list("  ") == []


def test_to_list_already_list():
    assert _to_list(["a", "b"]) == ["a", "b"]


def test_to_list_tuple():
    assert _to_list(("a", "b")) == ["a", "b"]


def test_to_list_json_array():
    assert _to_list('["a", "b"]') == ["a", "b"]


def test_to_list_json_string():
    assert _to_list('"hello"') == ["hello"]


def test_to_list_python_repr():
    assert _to_list("['a', 'b']") == ["a", "b"]


def test_to_list_plain_string():
    assert _to_list("some text") == ["some text"]


def test_to_list_number():
    assert _to_list(42) == ["42"]


def test_to_list_nested_json():
    assert _to_list('["Больные колени", "Большой вес"]') == ["Больные колени", "Большой вес"]
