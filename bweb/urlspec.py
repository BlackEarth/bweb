
from bl.dict import Dict
import tornado.web
from .route import Route
from .patterns import Patterns

class URLSpec(tornado.web.URLSpec, Route):

    def __init__(self, pattern, handler, patterns=Patterns, kwargs=None, name=None):
        pattern = Route.parse(pattern)
        tornado.web.URLSpec.__init__(self, pattern, handler, kwargs=kwargs, name=name)
        self.kwargs = Dict(**self.kwargs)

if __name__=="__main__":
    import doctest
    doctest.testmod()
