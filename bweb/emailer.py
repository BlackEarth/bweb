
import os, emails, tornado.template
from bl.dict import Dict

class Emailer(Dict):

    def __init__(self, template_path, **smtp):
        Dict.__init__(self, template_path=template_path, smtp=Dict(**smtp))
        self.template_loader = tornado.template.Loader(template_path)

