
import re                   # regular expressions
from bl.dict import Dict

from .patterns import Patterns
from .route import Route

class RouteMap(list):
    """A RouteMap is a list of dicts. If m is a RouteMap, m.match(url) will return
    a dict with key:value pairs indicating what routing keys to use for that url.
    For each route, the pattern is a regular expression, with additional routing
    key:value pairs to specify defaults. See example below. You can use whatever
    routing keys you want in your routes.

    That's it. No URL reversal is provided. What am I, your mother?
    Design your URLs carefully, and then don't change them once published.*
    If you do change them, you can edit your app -- grep is your friend.

    (* To mount your application at a different base url, put the server & path 
        in your site config. Then use this at the beginning of every url 
        in the application. The amp.wsgi.Application object will automatically 
        construct this as c.app.uri available to your application.)

    Here's an example session (using comparison for doctest happiness):
        >>> m = RouteMap([{'pattern': r"^/$", 'controller': 'webpages', 'action': 'view', 'name': 'home'}, \
                     {'pattern': r"^/(?P<controller>\w+)(\.(?P<fmt>\w+))?/?$", 'action': 'index'},    \
                     {'pattern': r"^/(?P<controller>\w+)/(?P<name>\w+)(\.(?P<fmt>\w+))?/?$", 'action': 'view'}, \
                     {'pattern': r"^/(?P<controller>\w+)/(?P<name>\w+)/(?P<action>\w+)/?$"},          \
                     {'pattern': r"^/.*$", 'script': 'errors/notfound.py'}])
        >>> m.match('') == None
        True
        >>> route = m.match('/')
        >>> route == {'controller': 'webpages', 'action': 'view', 'name': 'home'}
        True
        >>> route = m.match('/articles/')
        >>> route == {'controller': 'articles', 'action': 'index'}
        True
        >>> route = m.match('/articles.xml')
        >>> route == {'controller': 'articles', 'action': 'index', 'fmt': 'xml'}
        True
        >>> route = m.match('/articles/how_to_win')
        >>> route == {'controller': 'articles', 'action': 'view', 'name': 'how_to_win'}
        True
        >>> route = m.match('/articles/how_to_win.xml')
        >>> route == {'controller': 'articles', 'action': 'view', 'name': 'how_to_win', 'fmt': 'xml'}
        True
        >>> route = m.match('/articles/how_to_lose/del')
        >>> route == {'controller': 'articles', 'action': 'del', 'name': 'how_to_lose'}
        True
        >>> route = m.match('/someplace/else/that/I/dont/know/about')
        >>> route == {'script': 'errors/notfound.py'}
        True
    """

    def __init__(self, routes):
        """You can define a routemap (a list of dicts) on initialization."""
        for r in routes:
            self.append(Route(**r))

    def match(self, url):
        """Given a url, returns a dict indicating how to handle the request."""
        for rt in self:                         # for each route,
            matchdata = rt.regex.match(url)    # see if it matches the url -- CASE-INSENSITIVE
            if matchdata:                       # if so, put routing info in a dict and return it
                d = Dict()                      # don't operate directly on the route! Bad side-effects would ensue (because Python uses call-by-reference).
                d.update(**rt)                  # include everything that is in the route
                d.pop('regex')                 # but don't include the compiled regex
                d.pop('pattern')                # or the pattern, for that matter
                mdd = matchdata.groupdict()
                for k in mdd:                   # include named groups from match data
                    if mdd[k] is not None:      # except for None values
                        d[k] = mdd[k]
                return d

# ---------------------------------------------------------------------------
# -- TESTS --
def test_Map():
    """ Build a map, then try matches.
    >>> m = RouteMap([{'pattern': '^/$'}])
    >>> m.match('') == None
    True
    >>> m.match('/') == {}
    True
    """

# To test this module, do "python routes.py" from the command line and see what you get. No output => success.
if __name__ == "__main__":
    import doctest
    doctest.testmod()
