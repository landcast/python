import pytest
from mockito import mock, verify

from helloworld import helloworld


class Test_HelloWorld:

    def test_should_issue_hello_world_message(self):
        out = mock()
        helloworld(out)
        verify(out).write("Hello world of Python\n")


if __name__ == '__main__':
    pytest.main()
