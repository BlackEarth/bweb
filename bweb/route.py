
import re
from bl.dict import Dict
from .patterns import Patterns

class Route(Dict):
    def __init__(self, pattern, patterns=Patterns, **args):
        """Take a given pattern and return a Route object, which is used by RouteMap to create a route map.
        pattern: a url pattern, with named args in brackets: {var}
                name can take pattern indicator: {var:int}
                defaults to {var:slug}
        args: give default values for other variables
            handler: the name of the handler
            action: the name of the handler method to use
        Example:
        >>> routes = [Route("/{handler:slug}/"),
        ...           Route("/users/{username:slug}/", handler='users')]
        >>> for route in routes: print(route.pattern, "(handler=%s)" % route.handler)
        ^/(?P<handler>[\w\$\-\_\.\+\!\*\(\)\, %%@]+)/?$ (handler=None)
        ^/users/(?P<username>[\w\$\-\_\.\+\!\*\(\)\, %%@]+)/?$ (handler=users)
        """
        Dict.__init__(self, **args)
        self.pattern = self.parse(pattern, patterns=patterns)
        self.regex = self.compile(self.pattern)

    @classmethod
    def parse(C, pattern, patterns=Patterns):
        "Substitute with patterns"
        pattern = re.sub(r"\{(%(name)s)\}" % patterns, r"{\1:slug}", pattern, flags=re.U+re.I)                  # default name:slug
        pattern = re.sub(r"\{(%(name)s):(%(name)s)\}" % patterns, r"(?P<\1>%(\2)s)", pattern, flags=re.U+re.I)  # convert
            
        if pattern[-1] == '/': pattern += "?"     # make trailing slash optional
        pattern = "^" + pattern + "$"             # the pattern is the whole URL
        pattern = pattern % patterns
        return pattern

    @classmethod
    def compile(self, pattern):
        return re.compile(pattern, re.U)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
