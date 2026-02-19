from greet_package import greet


def test_greet():
    assert greet("World") == "Hello, World!"
