# coding=utf-8

# content of test_example.py
# Check PyTest documentation for more - https://docs.pytest.org/en/6.2.x/contents.html

def f():
    return 3

def test_that_succeeds():
    assert f() == 3
