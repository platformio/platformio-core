import json
from ..dispatcher import Dispatcher
from ..manager import AsyncJSONRPCResponseManager

class CommonBackend:
    def __init__(self, serialize=json.dumps, deserialize=json.loads):
        self.manager = AsyncJSONRPCResponseManager(
            Dispatcher(),
            serialize=serialize,
            deserialize=deserialize
        )

    def add_class(self, *args, **kwargs):
        return self.manager.dispatcher.add_class(*args, **kwargs)
    
    def add_object(self, *args, **kwargs):
        return self.manager.dispatcher.add_object(*args, **kwargs)

    def add_function(self, *args, **kwargs):
        return self.manager.dispatcher.add_function(*args, **kwargs)
