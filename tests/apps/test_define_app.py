import asynctest

from jj.apps import BaseApp, define_app


class TestDefineApp(asynctest.TestCase):
    def test_define_app(self):
        self.assertTrue(issubclass(define_app(), BaseApp))

    def test_define_app_with_name(self):
        name = "CustomApp"
        app = define_app(name)
        self.assertEqual(app.__name__, name)
