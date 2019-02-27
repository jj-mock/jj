import asynctest
from asynctest import CoroutineMock, Mock, sentinel, call
from multidict import MultiDict, CIMultiDict

from jj import Request
from jj.matchers import (AttributeMatcher, RequestMatcher, MethodMatcher,
                         PathMatcher, ParamMatcher, HeaderMatcher)


class TestRequestMatchers(asynctest.TestCase):
    async def test_abstract_request_matcher(self):
        resolver = Mock()
        matcher = RequestMatcher(resolver)

        request = Mock(Request)
        with self.assertRaises(NotImplementedError):
            await matcher.match(request)

    # MethodMatcher

    async def test_method_matcher_calls_resolver(self):
        resolver = Mock()
        matcher = MethodMatcher(resolver, "*")

        handler = CoroutineMock(return_value=sentinel.response)
        wrapper = matcher(handler)

        self.assertEqual(await wrapper(), sentinel.response)
        resolver.register_matcher.assert_called_once_with(matcher.match, handler)

    async def test_any_method_matcher(self):
        resolver = Mock()
        matcher = MethodMatcher(resolver, "*")

        request = Mock(Request, method="GET")
        self.assertTrue(await matcher.match(request))

        request = Mock(Request, method="POST")
        self.assertTrue(await matcher.match(request))

        request = Mock(Request, method="CUSTOM")
        self.assertTrue(await matcher.match(request))

    async def test_concrete_method_matcher(self):
        resolver = Mock()
        matcher = MethodMatcher(resolver, method="GET")

        request = Mock(Request, method="GET")
        self.assertTrue(await matcher.match(request))

        request = Mock(Request, method="get")
        self.assertFalse(await matcher.match(request))

        request = Mock(Request, method="POST")
        self.assertFalse(await matcher.match(request))

    async def test_method_matcher_with_custom_submatcher(self):
        resolver = Mock()
        submatcher = Mock(spec=AttributeMatcher)
        submatcher.match.side_effect = (False, True)

        matcher = MethodMatcher(resolver, submatcher)
        request = Mock(Request, method="GET")
        self.assertTrue(await matcher.match(request))

        submatcher.match.assert_has_calls([call("*"), call(request.method)])
        self.assertEqual(submatcher.match.call_count, 2)

    # PathMatcher

    async def test_path_matcher_calls_resolver(self):
        resolver = Mock()
        matcher = PathMatcher(resolver, "/")

        handler = CoroutineMock(return_value=sentinel.response)
        wrapper = matcher(handler)

        self.assertEqual(await wrapper(), sentinel.response)
        resolver.register_matcher.assert_called_once_with(matcher.match, handler)

    async def test_path_matcher_root_route(self):
        resolver = Mock()
        matcher = PathMatcher(resolver, path="/")

        request = Mock(Request, path="/")
        self.assertTrue(await matcher.match(request))

        request = Mock(Request, path="/smth")
        self.assertFalse(await matcher.match(request))

    async def test_path_matcher_parameterized_route(self):
        resolver = Mock()
        matcher = PathMatcher(resolver, "/users/{id}")

        request = Mock(Request, path="/users/1")
        self.assertTrue(await matcher.match(request))

        request = Mock(Request, path="/users")
        self.assertFalse(await matcher.match(request))

        request = Mock(Request, path="/users/1/profile")
        self.assertFalse(await matcher.match(request))

    async def test_path_matcher_regex_route(self):
        resolver = Mock()
        matcher = PathMatcher(resolver, "/{tail:.*}")

        request = Mock(Request, path="/")
        self.assertTrue(await matcher.match(request))

        request = Mock(Request, path="/smth")
        self.assertTrue(await matcher.match(request))

        request = Mock(Request, path="/users/1/profile")
        self.assertTrue(await matcher.match(request))

    async def test_path_matcher_with_custom_submatcher(self):
        resolver = Mock()
        submatcher = Mock(AttributeMatcher)
        submatcher.match.side_effect = (True,)

        matcher = PathMatcher(resolver, submatcher)
        request = Mock(Request)
        self.assertTrue(await matcher.match(request))

        submatcher.match.assert_called_once_with(request.path)

    # ParamMatcher

    async def test_param_matcher_calls_resolver(self):
        resolver = Mock()
        matcher = ParamMatcher(resolver, {})

        handler = CoroutineMock(return_value=sentinel.response)
        wrapper = matcher(handler)

        self.assertEqual(await wrapper(), sentinel.response)
        resolver.register_matcher.assert_called_once_with(matcher.match, handler)

    async def test_param_matcher_with_empty_keys(self):
        resolver = Mock()
        matcher_dict = ParamMatcher(resolver, {})
        matcher_tuple_list = ParamMatcher(resolver, [])

        request = Mock(Request, query={})
        self.assertTrue(await matcher_dict.match(request))
        self.assertTrue(await matcher_tuple_list.match(request))

        request = Mock(Request, query=MultiDict(key="val"))
        self.assertTrue(await matcher_dict.match(request))
        self.assertTrue(await matcher_tuple_list.match(request))

    async def test_param_matcher_with_single_key(self):
        resolver = Mock()
        matcher_dict = ParamMatcher(resolver, {"key": "val"})
        matcher_tuple_list = ParamMatcher(resolver, [("key", "val")])

        request = Mock(Request, query=MultiDict(key="val"))
        self.assertTrue(await matcher_dict.match(request))
        self.assertTrue(await matcher_tuple_list.match(request))

        request = Mock(Request, query=MultiDict([
            ("key", "val"),
            ("another_key", "another_val"),
        ]))
        self.assertTrue(await matcher_dict.match(request))
        self.assertTrue(await matcher_tuple_list.match(request))

        request = Mock(Request, query=MultiDict(key="not_val"))
        self.assertFalse(await matcher_dict.match(request))
        self.assertFalse(await matcher_tuple_list.match(request))

    async def test_param_matcher_with_multiple_keys(self):
        resolver = Mock()
        matcher_dict = ParamMatcher(resolver, {"key1": 1, "key2": 2})
        matcher_tuple_list = ParamMatcher(resolver, [("key1", 1), ("key2", 2)])

        request = Mock(Request, query=MultiDict([
            ("key1", 1),
            ("key2", 2),
        ]))
        self.assertTrue(await matcher_dict.match(request))
        self.assertTrue(await matcher_tuple_list.match(request))

        request = Mock(Request, query=MultiDict())
        self.assertFalse(await matcher_dict.match(request))
        self.assertFalse(await matcher_tuple_list.match(request))

        request = Mock(Request, query=MultiDict([
            ("key1", 1),
        ]))
        self.assertFalse(await matcher_dict.match(request))
        self.assertFalse(await matcher_tuple_list.match(request))

        request = Mock(Request, query=MultiDict([
            ("key1", 1),
            ("key2", 3),
        ]))
        self.assertFalse(await matcher_dict.match(request))
        self.assertFalse(await matcher_tuple_list.match(request))

        request = Mock(Request, query=MultiDict([
            ("key1", 1),
            ("key3", 3),
        ]))
        self.assertFalse(await matcher_dict.match(request))
        self.assertFalse(await matcher_tuple_list.match(request))

    async def test_param_matcher_with_case_sensitive_keys(self):
        resolver = Mock()
        matcher_dict = ParamMatcher(resolver, {"Key": "val"})
        matcher_tuple_list = ParamMatcher(resolver, [("Key", "val")])

        request = Mock(Request, query=MultiDict([
            ("Key", "val")
        ]))
        self.assertTrue(await matcher_dict.match(request))
        self.assertTrue(await matcher_tuple_list.match(request))

        request = Mock(Request, query=MultiDict([
            ("key", "val")
        ]))
        self.assertFalse(await matcher_dict.match(request))
        self.assertFalse(await matcher_tuple_list.match(request))

        request = Mock(Request, query=MultiDict([
            ("KEY", "val")
        ]))
        self.assertFalse(await matcher_dict.match(request))
        self.assertFalse(await matcher_tuple_list.match(request))

    async def test_param_matcher_with_multiple_values(self):
        resolver = Mock()

        matcher_dict = ParamMatcher(resolver, {"key": 1})
        matcher_tuple_list = ParamMatcher(resolver, [("key", 1)])
        request = Mock(Request, query=MultiDict([
            ("key", 1),
            ("key", 2)
        ]))
        self.assertTrue(await matcher_dict.match(request))
        self.assertTrue(await matcher_tuple_list.match(request))

        matcher_tuple_list = ParamMatcher(resolver, [("key", 1), ("key", 2)])
        request = Mock(Request, query=MultiDict([
            ("key", 1),
            ("key", 2)
        ]))
        self.assertTrue(await matcher_tuple_list.match(request))

        matcher_tuple_list = ParamMatcher(resolver, [("key", 1), ("key", 2)])
        request = Mock(Request, query=MultiDict([
            ("key", 1),
        ]))
        self.assertFalse(await matcher_tuple_list.match(request))

    async def test_param_matcher_with_custom_root_submatcher(self):
        resolver = Mock()
        submatcher = Mock(spec=AttributeMatcher)
        submatcher.match.return_value = True

        matcher = ParamMatcher(resolver, submatcher)
        request = Mock(Request, query=MultiDict([("key", 1)]))
        self.assertTrue(await matcher.match(request))

        submatcher.match.assert_called_once_with(request.query)

    async def test_param_matcher_with_custom_submatcher(self):
        resolver = Mock()
        submatcher = Mock(spec=AttributeMatcher)
        submatcher.match.return_value = True

        matcher = ParamMatcher(resolver, {
            "key1": submatcher,
            "key2": submatcher,
            "key3": 4,
        })
        request = Mock(Request, query=MultiDict([
            ("key1", 1),
            ("key1", 2),
            ("key2", 3),
            ("key3", 4),
            ("key4", 5),
        ]))
        self.assertTrue(await matcher.match(request))

        submatcher.match.assert_has_calls([
            call([1, 2]),
            call([3])
        ])
        self.assertEqual(submatcher.match.call_count, 2)

    # HeaderMatcher

    async def test_header_matcher_calls_resolver(self):
        resolver = Mock()
        matcher = HeaderMatcher(resolver, {})

        handler = CoroutineMock(return_value=sentinel.response)
        wrapper = matcher(handler)

        self.assertEqual(await wrapper(), sentinel.response)
        resolver.register_matcher.assert_called_once_with(matcher.match, handler)

    async def test_header_matcher_with_empty_keys(self):
        resolver = Mock()
        matcher_dict = HeaderMatcher(resolver, {})
        matcher_tuple_list = HeaderMatcher(resolver, [])

        request = Mock(Request, headers={})
        self.assertTrue(await matcher_dict.match(request))
        self.assertTrue(await matcher_tuple_list.match(request))

        request = Mock(Request, headers=CIMultiDict(key="val"))
        self.assertTrue(await matcher_dict.match(request))
        self.assertTrue(await matcher_tuple_list.match(request))

    async def test_header_matcher_with_single_key(self):
        resolver = Mock()
        matcher_dict = HeaderMatcher(resolver, {"key": "val"})
        matcher_tuple_list = HeaderMatcher(resolver, [("key", "val")])

        request = Mock(Request, headers=CIMultiDict(key="val"))
        self.assertTrue(await matcher_dict.match(request))
        self.assertTrue(await matcher_tuple_list.match(request))

        request = Mock(Request, headers=CIMultiDict([
            ("key", "val"),
            ("another_key", "another_val"),
        ]))
        self.assertTrue(await matcher_dict.match(request))
        self.assertTrue(await matcher_tuple_list.match(request))

        request = Mock(Request, headers=CIMultiDict(key="not_val"))
        self.assertFalse(await matcher_dict.match(request))
        self.assertFalse(await matcher_tuple_list.match(request))

    async def test_header_matcher_with_multiple_keys(self):
        resolver = Mock()
        matcher_dict = HeaderMatcher(resolver, {"key1": 1, "key2": 2})
        matcher_tuple_list = HeaderMatcher(resolver, [("key1", 1), ("key2", 2)])

        request = Mock(Request, headers=CIMultiDict([
            ("key1", 1),
            ("key2", 2),
        ]))
        self.assertTrue(await matcher_dict.match(request))
        self.assertTrue(await matcher_tuple_list.match(request))

        request = Mock(Request, headers=CIMultiDict())
        self.assertFalse(await matcher_dict.match(request))
        self.assertFalse(await matcher_tuple_list.match(request))

        request = Mock(Request, headers=CIMultiDict([
            ("key1", 1),
        ]))
        self.assertFalse(await matcher_dict.match(request))
        self.assertFalse(await matcher_tuple_list.match(request))

        request = Mock(Request, headers=CIMultiDict([
            ("key1", 1),
            ("key2", 3),
        ]))
        self.assertFalse(await matcher_dict.match(request))
        self.assertFalse(await matcher_tuple_list.match(request))

        request = Mock(Request, headers=CIMultiDict([
            ("key1", 1),
            ("key3", 3),
        ]))
        self.assertFalse(await matcher_dict.match(request))
        self.assertFalse(await matcher_tuple_list.match(request))

    async def test_header_matcher_with_case_sensitive_keys(self):
        resolver = Mock()
        matcher_dict = HeaderMatcher(resolver, {"Key": "val"})
        matcher_tuple_list = HeaderMatcher(resolver, [("Key", "val")])

        request = Mock(Request, headers=CIMultiDict([
            ("Key", "val")
        ]))
        self.assertTrue(await matcher_dict.match(request))
        self.assertTrue(await matcher_tuple_list.match(request))

        request = Mock(Request, headers=CIMultiDict([
            ("key", "val")
        ]))
        self.assertTrue(await matcher_dict.match(request))
        self.assertTrue(await matcher_tuple_list.match(request))

        request = Mock(Request, headers=CIMultiDict([
            ("KEY", "val")
        ]))
        self.assertTrue(await matcher_dict.match(request))
        self.assertTrue(await matcher_tuple_list.match(request))

    async def test_header_matcher_with_multiple_values(self):
        resolver = Mock()

        matcher_dict = HeaderMatcher(resolver, {"key": 1})
        matcher_tuple_list = HeaderMatcher(resolver, [("key", 1)])
        request = Mock(Request, headers=CIMultiDict([
            ("key", 1),
            ("key", 2)
        ]))
        self.assertTrue(await matcher_dict.match(request))
        self.assertTrue(await matcher_tuple_list.match(request))

        matcher_tuple_list = HeaderMatcher(resolver, [("key", 1), ("key", 2)])
        request = Mock(Request, headers=CIMultiDict([
            ("key", 1),
            ("key", 2)
        ]))
        self.assertTrue(await matcher_tuple_list.match(request))

        matcher_tuple_list = HeaderMatcher(resolver, [("key", 1), ("key", 2)])
        request = Mock(Request, headers=CIMultiDict([
            ("key", 1),
        ]))
        self.assertFalse(await matcher_tuple_list.match(request))

    async def test_header_matcher_with_custom_root_submatcher(self):
        resolver = Mock()
        submatcher = Mock(spec=AttributeMatcher)
        submatcher.match.return_value = True

        matcher = HeaderMatcher(resolver, submatcher)
        request = Mock(Request, headers=CIMultiDict([("key", 1)]))
        self.assertTrue(await matcher.match(request))

        submatcher.match.assert_called_once_with(request.headers)

    async def test_header_matcher_with_custom_submatcher(self):
        resolver = Mock()
        submatcher = Mock(spec=AttributeMatcher)
        submatcher.match.return_value = True

        matcher = HeaderMatcher(resolver, {
            "key1": submatcher,
            "key2": submatcher,
            "key3": 4,
        })
        request = Mock(Request, headers=CIMultiDict([
            ("key1", 1),
            ("key1", 2),
            ("key2", 3),
            ("key3", 4),
            ("key4", 5),
        ]))
        self.assertTrue(await matcher.match(request))

        submatcher.match.assert_has_calls([
            call([1, 2]),
            call([3])
        ])
        self.assertEqual(submatcher.match.call_count, 2)
