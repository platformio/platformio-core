import argparse
import asyncio
import json
import logging
import importlib.util
import sys
from inspect import getmembers, isfunction
from ajsonrpc import __version__
from ajsonrpc.dispatcher import Dispatcher
from ajsonrpc.manager import AsyncJSONRPCResponseManager


logger = logging.getLogger(__name__)

# Helper funciont to create asyncio task
# see: https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task
if sys.version_info >= (3, 7):
    create_task = asyncio.create_task
else:
    create_task = asyncio.ensure_future


class JSONRPCProtocol(asyncio.Protocol):
    def __init__(self, json_rpc_manager):
        self.json_rpc_manager = json_rpc_manager

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        message = data.decode()
        request_method, request_message = message.split('\r\n', 1)
        if not request_method.startswith('POST'):
            logger.warning('Incorrect HTTP method, should be POST')

        _, payload = request_message.split('\r\n\r\n', 1)
        task = create_task(self.json_rpc_manager.get_payload_for_payload(payload))
        task.add_done_callback(self.handle_task_result)
    
    def handle_task_result(self, task):
        res = task.result()
        self.transport.write((
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n"
            "\r\n"
            +  str(res)
        ).encode("utf-8"))

        logger.info('Close the client socket')
        self.transport.close()


def main():
    """Usage: % examples.methods"""
    parser = argparse.ArgumentParser(
        add_help=True,
        description="Start async JSON-RPC 2.0 server")
    parser.add_argument(
        '--version', action='version',
        version='%(prog)s {version}'.format(version=__version__))
    parser.add_argument("--host", dest="host", default="127.0.0.1")
    parser.add_argument("--port", dest="port")
    parser.add_argument('module')

    args = parser.parse_args()

    spec = importlib.util.spec_from_file_location("module", args.module)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # get functions from the module
    methods = getmembers(module, isfunction)
    logger.info('Extracted methods: {}'.format(methods))
    dispatcher = Dispatcher(dict(methods))

    json_rpc_manager = AsyncJSONRPCResponseManager(dispatcher=dispatcher)
    loop = asyncio.get_event_loop()
    # Each client connection will create a new protocol instance
    coro = loop.create_server(
        lambda: JSONRPCProtocol(json_rpc_manager),
        host=args.host,
        port=args.port
    )
    server = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C is pressed
    logger.info('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == '__main__':
    # setup console logging
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(module)s:%(lineno)d] %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    main()
