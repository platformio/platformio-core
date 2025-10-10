"""Test Async JSON-RPC Response manager."""
import unittest
import json

from ..core import JSONRPC20Request, JSONRPC20Response, JSONRPC20MethodNotFound, JSONRPC20InvalidParams, JSONRPC20ServerError, JSONRPC20DispatchException
from ..manager import AsyncJSONRPCResponseManager


class TestAsyncJSONRPCResponseManager(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        def subtract(minuend, subtrahend):
            return minuend - subtrahend

        def raise_(e: Exception):
            raise e

        async def async_sum(*args):
            return sum(args)

        self.dispatcher = {
            "subtract": subtract,
            "async_sum": async_sum,
            "dispatch_exception": lambda: raise_(
                JSONRPC20DispatchException(
                    code=4000, message="error", data={"param": 1}
                )
            ),
            "unexpected_exception": lambda: raise_(ValueError("Unexpected")),
        }

        self.manager = AsyncJSONRPCResponseManager(dispatcher=self.dispatcher)

    async def test_get_response(self):
        req = JSONRPC20Request("subtract", params=[5, 3], id=0)
        res = await self.manager.get_response_for_request(req)
        self.assertTrue(isinstance(res, JSONRPC20Response))
        self.assertEqual(res.result, 2)

    async def test_get_response_notification(self):
        req = JSONRPC20Request("subtract", params=[5, 3], is_notification=True)
        res = await self.manager.get_response_for_request(req)
        self.assertIsNone(res)

    async def test_get_async_response(self):
        req = JSONRPC20Request("async_sum", params=[1, 2, 3], id=0)
        res = await self.manager.get_response_for_request(req)
        self.assertTrue(isinstance(res, JSONRPC20Response))
        self.assertEqual(res.result, 6)

    async def test_get_response_method_not_found(self):
        req = JSONRPC20Request("does_not_exist", id=0)
        res = await self.manager.get_response_for_request(req)
        self.assertTrue(isinstance(res, JSONRPC20Response))
        self.assertEqual(res.error, JSONRPC20MethodNotFound())
        self.assertEqual(res.id, req.id)

    async def test_get_response_method_not_found_notification(self):
        req = JSONRPC20Request("does_not_exist", is_notification=True)
        res = await self.manager.get_response_for_request(req)
        self.assertIsNone(res)

    async def test_get_response_incorrect_arguments(self):
        req = JSONRPC20Request("subtract", params=[0], id=0)
        res = await self.manager.get_response_for_request(req)
        self.assertTrue(isinstance(res, JSONRPC20Response))
        self.assertEqual(res.error, JSONRPC20InvalidParams())
        self.assertEqual(res.id, req.id)

    async def test_get_response_incorrect_arguments_notification(self):
        req = JSONRPC20Request("subtract", params=[0], is_notification=True)
        res = await self.manager.get_response_for_request(req)
        self.assertIsNone(res)

    async def test_get_response_method_expected_error(self):
        req = JSONRPC20Request("dispatch_exception", id=0)
        res = await self.manager.get_response_for_request(req)
        self.assertTrue(isinstance(res, JSONRPC20Response))
        self.assertEqual(res.error.body, dict(code=4000, message="error", data={"param": 1}))
        self.assertEqual(res.id, req.id)

    async def test_get_response_method_expected_error_notification(self):
        req = JSONRPC20Request("dispatch_exception", is_notification=True)
        res = await self.manager.get_response_for_request(req)
        self.assertIsNone(res)

    async def test_get_response_method_unexpected_error(self):
        req = JSONRPC20Request("unexpected_exception", id=0)
        res = await self.manager.get_response_for_request(req)
        self.assertTrue(isinstance(res, JSONRPC20Response))
        self.assertEqual(res.error, JSONRPC20ServerError())
        self.assertEqual(res.id, req.id)

    async def test_get_response_method_unexpected_error_notification(self):
        req = JSONRPC20Request("unexpected_exception", is_notification=True)
        res = await self.manager.get_response_for_request(req)
        self.assertIsNone(res)
    
    async def test_get_response_for_payload_batch(self):
        response = await self.manager.get_response_for_payload(json.dumps([
            {"jsonrpc": "2.0", "method": "subtract", "params": [3, 4], "id": 1},
            {"jsonrpc": "2.0"}
        ]))
        self.assertEqual(
            response.body,
            [
                {"jsonrpc": "2.0", "result": -1, "id": 1},
                {
                    "jsonrpc": "2.0",
                    "error": {"code": -32600, "message": "Invalid Request"},
                    "id": None
                },
            ]
        )

    async def test_verbose_error(self):
        manager = AsyncJSONRPCResponseManager(
            dispatcher=self.dispatcher, is_server_error_verbose=True)
        req = JSONRPC20Request("unexpected_exception", id=0)
        res = await manager.get_response_for_request(req)
        self.assertEqual(
            res.error.data,
            {'type': 'ValueError', 'args': ('Unexpected',), 'message': 'Unexpected'}
        )

        manager.is_server_error_verbose = False
        res = await manager.get_response_for_request(req)
        self.assertIsNone(res.error.data)

    #############################################
    # Test examples from https://www.jsonrpc.org/specification
    #############################################

    async def test_examples_positional_parameters(self):
        response1 = await self.manager.get_response_for_payload(
            '{"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}'
        )
        self.assertEqual(response1.body, {"jsonrpc": "2.0", "result": 19, "id": 1})

        response2 = await self.manager.get_response_for_payload(
            '{"jsonrpc": "2.0", "method": "subtract", "params": [23, 42], "id": 2}'
        )
        self.assertEqual(response2.body, {"jsonrpc": "2.0", "result": -19, "id": 2})

    async def test_examples_named_parameters(self):
        response1 = await self.manager.get_response_for_payload(
            '{"jsonrpc": "2.0", "method": "subtract", "params": {"subtrahend": 23, "minuend": 42}, "id": 3}'
        )
        self.assertEqual(response1.body, {"jsonrpc": "2.0", "result": 19, "id": 3})

        response2 = await self.manager.get_response_for_payload(
            '{"jsonrpc": "2.0", "method": "subtract", "params": {"minuend": 42, "subtrahend": 23}, "id": 4}'
        )
        self.assertEqual(response2.body, {"jsonrpc": "2.0", "result": 19, "id": 4})

    async def test_examples_notification(self):
        response1 = await self.manager.get_response_for_payload(
            '{"jsonrpc": "2.0", "method": "update", "params": [1,2,3,4,5]}'
        )
        self.assertIsNone(response1)

        response2 = await self.manager.get_response_for_payload(
            '{"jsonrpc": "2.0", "method": "foobar"}'
        )
        self.assertIsNone(response2)

    async def test_examples_rpc_call_of_nonexistent_method(self):
        response = await self.manager.get_response_for_payload(
            '{"jsonrpc": "2.0", "method": "foobar", "id": "1"}'
        )
        self.assertEqual(response.body, {"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": "1"})

    async def test_exampels_rpc_call_with_invalid_json(self):
        response = await self.manager.get_response_for_payload(
            '{"jsonrpc": "2.0", "method": "foobar, "params": "bar", "baz]'
        )
        self.assertEqual(response.body, {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None})

    async def test_examples_rpc_call_with_invalid_request_object(self):
        response = await self.manager.get_response_for_payload(
            '{"jsonrpc": "2.0", "method": 1, "params": "bar"}'
        )
        self.assertEqual(response.body, {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": None})

    async def test_examples_rpc_call_batch_invalid_json(self):
        response = await self.manager.get_response_for_payload(
            """[
                {"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], "id": "1"},
                {"jsonrpc": "2.0", "method"
            ]"""
        )
        self.assertEqual(response.body, {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None})

    async def test_examples_rpc_call_with_an_empty_array(self):
        response = await self.manager.get_response_for_payload('[]')
        self.assertEqual(response.body, {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": None})

    async def test_examples_rpc_call_with_an_invalid_batch_but_not_empty(self):
        response = await self.manager.get_response_for_payload('[1]')
        self.assertEqual(response.body, [{"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": None}])

    async def test_examples_rpc_call_with_invalid_batch(self):
        response = await self.manager.get_response_for_payload('[1,2,3]')
        self.assertEqual(response.body, [
            {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": None},
            {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": None},
            {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": None}
        ])

    async def test_examples_rpc_call_batch(self):
        dispatcher = {
            "sum": lambda *values: sum(values),
            "subtract": lambda a, b: a - b,
            "get_data": lambda: ["hello", 5],
        }
        manager = AsyncJSONRPCResponseManager(dispatcher=dispatcher)

        response = await manager.get_response_for_payload(json.dumps([
            {"jsonrpc": "2.0", "method": "sum", "params": [1, 2, 4], "id": "1"},
            {"jsonrpc": "2.0", "method": "notify_hello", "params": [7]},
            {"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": "2"},
            {"foo": "boo"},
            {"jsonrpc": "2.0", "method": "foo.get", "params": {"name": "myself"}, "id": "5"},
            {"jsonrpc": "2.0", "method": "get_data", "id": "9"},
        ]))

        self.assertEqual(response.body, [
            {"jsonrpc": "2.0", "result": 7, "id": "1"},
            {"jsonrpc": "2.0", "result": 19, "id": "2"},
            {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": None},
            {"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": "5"},
            {"jsonrpc": "2.0", "result": ["hello", 5], "id": "9"}
        ])

    async def test_examples_rpc_call_batch_all_notifications(self):
        response = await self.manager.get_response_for_payload(json.dumps([
            {"jsonrpc": "2.0", "method": "notify_sum", "params": [1, 2, 4]},
            {"jsonrpc": "2.0", "method": "notify_hello", "params": [7]},
        ]))
        self.assertIsNone(response)
