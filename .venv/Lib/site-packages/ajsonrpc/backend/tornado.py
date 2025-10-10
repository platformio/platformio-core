import tornado.web
from .common import CommonBackend


class JSONRPCTornado(CommonBackend):
    @property
    def handler(self):
        """Get Tornado Handler"""
        manager = self.manager

        class JSONRPCTornadoHandler(tornado.web.RequestHandler):
            async def post(self):
                self.set_header("Content-Type", "application/json")
                payload = await manager.get_payload_for_payload(self.request.body)
                self.write(payload)
        
        return JSONRPCTornadoHandler

