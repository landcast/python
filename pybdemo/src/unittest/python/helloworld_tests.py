from mockito import mock, verify
import unittest

from helloworld import helloworld


class HelloWorldTest(unittest.TestCase):

    def setUp(self):
        print('overriding unittest.setUp() method')

    def tearDown(self):
        print('overriding unittest.tearDown() method')

    def test_should_issue_hello_world_message(self):
        out = mock()
        helloworld(out)
        verify(out).write("Hello world of Python\n")
