
"""Patterns used in routing requests. 
Usage: 
>>> print("/path/(?P<id>{slug})".format(**Patterns))   # with str.format()
/path/(?P<id>[\w\$\-\_\.\+\!\*\(\)\, %%@]+)
>>> print("/path/(?P<id>%(slug)s)" % Patterns)         # with %-style replacement
/path/(?P<id>[\w\$\-\_\.\+\!\*\(\)\, %%@]+)
"""

from bl.dict import Dict

Patterns = Dict(**{
    'int': r'[0-9]+',                           # int: integer
    'dec': r'[0-9\.,]+',                        # dec: decimal
    'slug': r'[\w\$\-\_\.\+\!\*\(\)\, %%@]+',   # slug: a part of a url between /
    'path': r'[\w\$\-\_\.\+\!\*\(\)\, %%@/]+',  # path: anything legal in a path
    'word': r'[\w\-]+',                         # word: starts with letter or _ or -, + word chars
    'name': r'[a-zA-Z_][a-zA-Z0-9_]+',          # name: starts with letter or _, then letter, number, or _
    'hex': r'[0-9a-f]+',                        # hex: hexidecimal number
    })

if __name__=="__main__":
    import doctest
    doctest.testmod()
