import unittest
from ..dispatcher import Dispatcher


class Math:
    @staticmethod
    def sum(a, b):
        return a + b

    @classmethod
    def diff(cls, a, b):
        return a - b

    def mul(self, a, b):
        return a * b


class TestDispatcher(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(len(Dispatcher()), 0)

    def test_add_function(self):
        d = Dispatcher()

        @d.add_function
        def one():
            return 1

        def two():
            return 2

        d.add_function(two)
        d.add_function(two, name="two_alias")

        self.assertIn("one", d)
        self.assertEqual(d["one"](), 1)
        self.assertIsNotNone(one)  # do not remove function from the scope
        self.assertIn("two", d)
        self.assertIn("two_alias", d)

    def test_class(self):
        d1 = Dispatcher()
        d1.add_class(Math)
        self.assertIn("math.sum", d1)
        self.assertIn("math.diff", d1)
        self.assertIn("math.mul", d1)
        self.assertEqual(d1["math.sum"](3, 8), 11)
        self.assertEqual(d1["math.diff"](6, 9), -3)
        self.assertEqual(d1["math.mul"](2, 3), 6)

        d2 = Dispatcher(Math)
        self.assertNotIn("__class__", d2)
        self.assertEqual(d1.keys(), d2.keys())
        for method in ["math.sum", "math.diff"]:
            self.assertEqual(d1[method], d2[method])

    def test_class_prefix(self):
        d = Dispatcher(Math, prefix="")
        self.assertIn("sum", d)
        self.assertNotIn("math.sum", d)

    def test_object(self):
        math = Math()
        d1 = Dispatcher()
        d1.add_object(math)
        self.assertIn("math.sum", d1)
        self.assertIn("math.diff", d1)
        self.assertEqual(d1["math.sum"](3, 8), 11)
        self.assertEqual(d1["math.diff"](6, 9), -3)

        d2 = Dispatcher(math)
        self.assertNotIn("__class__", d2)
        self.assertEqual(d1, d2)

    def test_object_prefix(self):
        d = Dispatcher(Math(), prefix="")
        self.assertIn("sum", d)
        self.assertNotIn("math.sum", d)

    def test_add_dict(self):
        d = Dispatcher()
        d.add_prototype({"sum": lambda *args: sum(args)}, "util.")

        self.assertIn("util.sum", d)
        self.assertEqual(d["util.sum"](13, -2), 11)

    def test_init_from_dict(self):
        d = Dispatcher({
            "one": lambda: 1,
            "two": lambda: 2,
        })

        self.assertIn("one", d)
        self.assertIn("two", d)

    def test_del_method(self):
        d = Dispatcher()
        d["method"] = lambda: ""
        self.assertIn("method", d)

        del d["method"]
        self.assertNotIn("method", d)

    def test_to_dict(self):
        d = Dispatcher()

        def func():
            return ""

        d["method"] = func
        self.assertEqual(dict(d), {"method": func})

    def test__getattr_function(self):
        # class
        self.assertEqual(Dispatcher._getattr_function(Math, "sum")(3, 2), 5)
        self.assertEqual(Dispatcher._getattr_function(Math, "diff")(3, 2), 1)
        self.assertEqual(Dispatcher._getattr_function(Math, "mul")(3, 2), 6)

        # object
        self.assertEqual(Dispatcher._getattr_function(Math(), "sum")(3, 2), 5)
        self.assertEqual(Dispatcher._getattr_function(Math(), "diff")(3, 2), 1)
        self.assertEqual(Dispatcher._getattr_function(Math(), "mul")(3, 2), 6)
