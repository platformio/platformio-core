import unittest
import warnings

from ..core import (JSONRPC20BatchRequest, JSONRPC20BatchResponse,
                    JSONRPC20Error, JSONRPC20InternalError,
                    JSONRPC20InvalidParams, JSONRPC20InvalidRequest,
                    JSONRPC20MethodNotFound, JSONRPC20ParseError,
                    JSONRPC20Request, JSONRPC20RequestIdWarning,
                    JSONRPC20Response, JSONRPC20ServerError)


class TestJSONRPC20Request(unittest.TestCase):

    """Test JSONRPC20Request.

    On creation and after modification the request object has to be valid. As
    these scenarios are almost identical, test both in test cases.

    """

    #############################################
    # "method" tests
    #############################################

    def test_method_validation_correct(self):
        r = JSONRPC20Request(method="valid", id=0)
        self.assertEqual(r.method, "valid")
        r.method = "also_valid"
        self.assertEqual(r.method, "also_valid")

    def test_method_validation_not_str(self):
        r = JSONRPC20Request(method="valid", id=0)

        with self.assertRaises(ValueError):
            JSONRPC20Request(method=[], id=0)

        with self.assertRaises(ValueError):
            r.method = []

        # invalid setters should not modify the object
        self.assertEqual(r.method, "valid")

        with self.assertRaises(ValueError):
            JSONRPC20Request(method={}, id=0)

        with self.assertRaises(ValueError):
            r.method = {}

    def test_method_validation_invalid_rpc_prefix(self):
        """ Test method SHOULD NOT starts with rpc."""
        r = JSONRPC20Request(method="valid", id=0)

        with self.assertRaises(ValueError):
            JSONRPC20Request(method="rpc.", id=0)

        with self.assertRaises(ValueError):
            r.method = "rpc."

        # invalid setters should not modify the object
        self.assertEqual(r.method, "valid")

        with self.assertRaises(ValueError):
            JSONRPC20Request(method="rpc.test", id=0)

        with self.assertRaises(ValueError):
            r.method = "rpc.test"

        JSONRPC20Request(method="rpcvalid", id=0)
        JSONRPC20Request(method="rpc", id=0)

    #############################################
    # "params" tests
    #############################################

    def test_params_validation_none(self):
        r1 = JSONRPC20Request("null_params", params=None, id=1)
        self.assertFalse("params" in r1.body)

        # Remove params
        r2 = JSONRPC20Request("null_params", params=[], id=2)
        self.assertTrue("params" in r2.body)
        del r2.params
        self.assertFalse("params" in r2.body)

    def test_params_validation_list(self):
        r = JSONRPC20Request("list", params=[], id=0)
        self.assertEqual(r.params, [])
        r.params = [0, 1]
        self.assertEqual(r.params, [0, 1])

    def test_params_validation_tuple(self):
        r = JSONRPC20Request("tuple", params=(), id=0)
        self.assertEqual(r.params, ())  # keep the same iterable
        r.params = (0, 1)
        self.assertEqual(r.params, (0, 1))

    def test_params_validation_iterable(self):
        r1 = JSONRPC20Request("string_params", params="string", id=1)
        self.assertEqual(r1.params, "string")
        r1.params = "another string"
        self.assertEqual(r1.params, "another string")

        r2 = JSONRPC20Request("range_params", params=range(1), id=2)
        self.assertEqual(r2.params, range(1))
        r2.params = range(2)
        self.assertEqual(r2.params, range(2))

    def test_params_validation_dict(self):
        r1 = JSONRPC20Request("dict_params", params={}, id=1)
        self.assertEqual(r1.params, {})
        r1.params = {"a": 0}
        self.assertEqual(r1.params, {"a": 0})

        r2 = JSONRPC20Request("dict_params", params={"a": 0}, id=2)
        self.assertEqual(r2.params, {"a": 0})
        r2.params = {"a": {}}
        self.assertEqual(r2.params, {"a": {}})

    def test_params_validation_invalid(self):
        r = JSONRPC20Request("list", params=[], id=0)

        with self.assertRaises(ValueError):
            JSONRPC20Request("invalid_params", params=0, id=0)

        with self.assertRaises(ValueError):
            r.params = 0

        self.assertEqual(r.params, [])

    #############################################
    # "id" tests
    #############################################

    def test_id_validation_valid(self):
        r1 = JSONRPC20Request("string_id", id="id")
        self.assertEqual(r1.id, "id")
        r1.id = "another_id"
        self.assertEqual(r1.id, "another_id")

        r2 = JSONRPC20Request("int_id", id=0)
        self.assertEqual(r2.id, 0)
        r2.id = 1
        self.assertEqual(r2.id, 1)

        # Null ids are possible but discouraged. Omit id for notifications.
        with warnings.catch_warnings(record=True) as _warnings:
            warnings.simplefilter("always")
            JSONRPC20Request("null_id", id=None)
            assert len(_warnings) == 1
            assert issubclass(_warnings[-1].category, JSONRPC20RequestIdWarning)
            assert "Null as a value" in str(_warnings[-1].message)

        # Float ids are possible but discouraged
        with warnings.catch_warnings(record=True) as _warnings:
            warnings.simplefilter("always")
            JSONRPC20Request("float_id", id=0.1)

            assert len(_warnings) == 1
            assert issubclass(_warnings[-1].category, JSONRPC20RequestIdWarning)
            assert "Fractional parts" in str(_warnings[-1].message)


    def test_id_validation_invalid(self):
        r = JSONRPC20Request("valid_id", id=0)

        with self.assertRaises(ValueError):
            JSONRPC20Request("list_id", id=[])

        with self.assertRaises(ValueError):
            r.id = []

        self.assertEqual(r.id, 0)

        with self.assertRaises(ValueError):
            JSONRPC20Request("dict_id", id={})

        with self.assertRaises(ValueError):
            r.id = {}

    #############################################
    # Notification tests
    #############################################

    def test_notification_init(self):
        r = JSONRPC20Request("notification", is_notification=True)
        self.assertTrue(r.is_notification)
        with self.assertRaises(KeyError):
            r.id

    def test_notification_conversion(self):
        r = JSONRPC20Request("notification", id=0)
        self.assertFalse(r.is_notification)
        del r.id
        self.assertTrue(r.is_notification)

    #############################################
    # Auxiliary methods tests
    #############################################

    def test_request_args(self):
        self.assertEqual(JSONRPC20Request("add", id=0).args, [])
        self.assertEqual(JSONRPC20Request("add", [], id=0).args, [])
        self.assertEqual(JSONRPC20Request("add", "str", id=0).args, ["s", "t", "r"])
        self.assertEqual(JSONRPC20Request("add", {"a": 1}, id=0).args, [])
        self.assertEqual(JSONRPC20Request("add", [1, 2], id=0).args, [1, 2])

    def test_request_kwargs(self):
        self.assertEqual(JSONRPC20Request("add", id=0).kwargs, {})
        self.assertEqual(JSONRPC20Request("add", [1, 2], id=0).kwargs, {})
        self.assertEqual(JSONRPC20Request("add", {}, id=0).kwargs, {})
        self.assertEqual(JSONRPC20Request("add", {"a": 1}, id=0).kwargs, {"a": 1})

    #############################################
    # body methods tests
    #############################################
    def test_body_validation(self):
        r = JSONRPC20Request(method="valid", id=0)
        self.assertEqual(
            r.body,
            {
                "jsonrpc": "2.0",
                "method": "valid",
                "id": 0,
            }
        )
        r.body = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "new",
        }
        self.assertEqual(r.id, 1)
        self.assertEqual(r.method, "new")

        # body has to have "jsonrpc" in it
        with self.assertRaises(ValueError):
            r.body = {"id": 1, "method": "new"}

        with self.assertRaises(ValueError):
            r.body = {
                "jsonrpc": "2.0",
                "id": [],
                "method": 0,
                "params": 0,
            }

        self.assertEqual(r.id, 1)
        self.assertEqual(r.method, "new")


class TestJSONRPC20BatchRequest(unittest.TestCase):
    def test_init(self):
        br = JSONRPC20BatchRequest()
        self.assertEqual(len(br), 0)

        br.append(JSONRPC20Request("first", id=1))
        br.extend([JSONRPC20Request("second", id=2)])
        self.assertEqual(len(br), 2)
        self.assertEqual(br[-1].method, "second")


class TestJSONRPC20Error(unittest.TestCase):

    """Test JSONRPC20Error.

    On creation and after modification the request object has to be valid. As
    these scenarios are almost identical, test both in test cases.

    """

    #############################################
    # "code" tests
    #############################################

    def test_code_validation_valid_numeric(self):
        e = JSONRPC20Error(code=0, message="error")
        self.assertEqual(e.code, 0)
        # Allow numeric codes. Though, prefer using integers
        e.code = 1
        self.assertEqual(e.code, 1)

    def test_code_validation_not_number(self):
        e = JSONRPC20Error(code=0, message="error")

        with self.assertRaises(ValueError):
            JSONRPC20Error(code="0", message="error")

        with self.assertRaises(ValueError):
            e.code = "0"

    #############################################
    # "message" tests
    #############################################

    def test_message_validation_valid_str(self):
        e = JSONRPC20Error(code=0, message="error")
        self.assertEqual(e.message, "error")
        e.message = "specific error"
        self.assertEqual(e.message, "specific error")

    def test_message_validation_not_str(self):
        e = JSONRPC20Error(code=0, message="error")

        with self.assertRaises(ValueError):
            JSONRPC20Error(code=0, message=0)

        with self.assertRaises(ValueError):
            e.message = 0

    #############################################
    # "data" tests
    #############################################
    def test_data_validation_valid(self):
        e = JSONRPC20Error(code=0, message="error", data=0)
        self.assertEqual(e.data, 0)
        e.data = {"timestamp": 0}
        self.assertEqual(e.data, {"timestamp": 0})

    def test_could_not_change_code_message_predefined_errors(self):
        errors = [
            JSONRPC20ParseError(),
            JSONRPC20InvalidRequest(),
            JSONRPC20MethodNotFound(),
            JSONRPC20InvalidParams(),
            JSONRPC20InternalError(),
            JSONRPC20ServerError(),
        ]

        for error in errors:
            with self.assertRaises(NotImplementedError):
                error.code = 0

            with self.assertRaises(NotImplementedError):
                error.message = ""


class TestJSONRPC20Response(unittest.TestCase):
    def test_valid_result(self):
        response = JSONRPC20Response(result="valid")
        self.assertEqual(response.result, "valid")
        self.assertIsNone(response.error)
        self.assertEqual(
            response.body,
            {"jsonrpc": "2.0", "id": None, "result": "valid"}
        )

    def test_valid_error(self):
        error = JSONRPC20MethodNotFound()
        response = JSONRPC20Response(error=error)
        self.assertIsNone(response.result)
        self.assertEqual(response.error, error)
        self.assertEqual(
            response.body,
            {"jsonrpc": "2.0", "id": None, "error": error.body}
        )

    def test_set_valid_body(self):
        response = JSONRPC20Response(result="")
        response.body = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": 0,
                "message": "",
            }
        }
        self.assertIsInstance(response.error, JSONRPC20Error)

    def test_set_body_result_and_error(self):
        response = JSONRPC20Response(result="")
        with self.assertRaises(ValueError):
            response.body = {
                "jsonrpc": "2.0",
                "id": None,
                "result": "",
                "error": {
                    "code": 0,
                    "message": "",
                }
            }

        with self.assertRaises(ValueError):
            JSONRPC20Response(
                result="",
                error=JSONRPC20Error(code=0, message="")
            )

    @unittest.skip("TODO: Implement later")
    def test_set_body_error_correct_error_class(self):
        """Return error class matching pre-defined error codes."""
        response = JSONRPC20Response(result="")
        response.body = {
            "jsonrpc": "2.0",
            "id": None,
            "error": JSONRPC20MethodNotFound().body,
        }
        self.assertIsInstance(response.error, JSONRPC20MethodNotFound)


class TestJSONRPC20BatchResponse(unittest.TestCase):
    def test_init(self):
        batch = JSONRPC20BatchResponse()
        self.assertEqual(len(batch), 0)

        batch.append(JSONRPC20Response(result="first", id=1))
        batch.extend([JSONRPC20Response(result="second", id=2)])
        self.assertEqual(len(batch), 2)
        self.assertEqual(batch[-1].result, "second")
