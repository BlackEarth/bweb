
from bsql.model import Model

class RequestLog(Model):
    relation = 'request_log'
    pk = []     # no primary key needed for a logging table
