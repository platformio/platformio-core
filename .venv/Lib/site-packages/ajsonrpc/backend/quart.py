import json

from quart import Response, request
from .common import CommonBackend


class JSONRPCQuart(CommonBackend):
    @property
    def handler(self):
        """Get Quart Handler"""

        async def handle():
            request_body = await request.body
            response = await self.manager.get_response_for_payload(request_body)
            return Response(json.dumps(response.body), mimetype="application/json")

        return handle
