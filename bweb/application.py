# web server application
# -- tornado is the best way to create an asyncronous, real-time app in python.

import tornado.ioloop, tornado.web
from bl.dict import Dict

class Application(tornado.web.Application, Dict):
    def __init__(self, routes=None, default_host='', transforms=None, **settings):
        tornado.web.Application.__init__(self, routes, default_host=default_host, transforms=transforms)
        self.settings = Dict(**settings)

    def __call__(self, port=None):
        self.listen(port or (self.settings.Site or Dict()).port or 80)
        tornado.ioloop.IOLoop.instance().start()

