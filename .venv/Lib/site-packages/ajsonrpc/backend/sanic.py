from sanic.response import json as json_response
from .common import CommonBackend

class JSONRPCSanic(CommonBackend):    
    @property
    def handler(self):
        """Get Sanic Handler"""
        async def handle(request):
            response = await self.manager.get_response_for_payload(request.body)
            return json_response(response.body, dumps=self.manager.serialize)

        return handle
