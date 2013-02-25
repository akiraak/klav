# -*- coding:utf-8 -*-
import codecs
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, Session, Query
from sqlalchemy.ext.declarative import declarative_base#, Column
#from sqlalchemy.ext.mutable import Mutable
#from sqlalchemy.types import TypeDecorator, TEXT, VARCHAR
#from redis import StrictRedis
from flask import g, current_app
#import json

# workaround for oursql not understanding utf8mb4
codecs.register(lambda name: codecs.lookup('utf8') if name == 'utf8mb4' else None)

class FlaskSession(Session):
    def get_bind(self, mapper=None, clause=None):
        return current_app.db_engine


#redis = None

db_session = scoped_session(sessionmaker(class_=FlaskSession, autocommit=True, autoflush=False))
ModelBase = declarative_base()

default_table_args = {
    'mysql_engine': 'InnoDB',
    'mysql_charset': 'utf8'}

'''
def init_redis(app):
    global redis

    app.config.setdefault('REDIS_HOST', 'localhost')
    app.config.setdefault('REDIS_PORT', 6379)
    app.config.setdefault('REDIS_DB', 0)
    app.config.setdefault('REDIS_PASSWORD', None)

    redis = StrictRedis(host=app.config['REDIS_HOST'],
                  port=app.config['REDIS_PORT'],
                  db=app.config['REDIS_DB'],
                  password=app.config['REDIS_PASSWORD'])

    @app.before_request
    def remember_redis():
        g.redis = redis
'''


def init_db(app, dburi_key='DATABASE_URI'):
    app.db_engine = create_sa_engine(app.config[dburi_key])
    ModelBase.query = db_session.query_property()

    @app.after_request
    def shutdown_session(response):
        db_session.remove()
        return response


def create_sa_engine(dburi, **options):
    defaults = {
        'convert_unicode': True,
        'pool_recycle': 60 * 60,
        'encoding': 'utf8',
        }
    defaults.update(options)
    return create_engine(dburi, **defaults)


'''
def make_tables(app):
    ModelBase.metadata.create_all(bind=app.db_engine)


def raw_connect(app, dburi_key='DATABASE_URI'):
    import oursql
    from sqlalchemy.engine.url import make_url
    url = make_url(current_app.config[dburi_key])
    opts = {}
    for connect_key, url_key in [('host', 'host'), ('user', 'username'), ('passwd', 'password'), ('db', 'database'), ('port', 'port')]:
        if getattr(url, url_key):
            opts[connect_key] = getattr(url, url_key)
    return oursql.connect(**opts), opts


# SQLAlchemy custom types
class JSONEncodedDict(TypeDecorator):
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(value, ensure_ascii=False, encoding='utf8')

    def process_result_value(self, value, dialect):
        if not value:
            return None
        return json.loads(value)


class MutationDict(Mutable, dict):
    @classmethod
    def coerce(cls, key, value):
        "Convert plain dictionaries to MutationDict."

        if not isinstance(value, MutationDict):
            if isinstance(value, dict):
                return MutationDict(value)

            # this call will raise ValueError
            return Mutable.coerce(key, value)
        else:
            return value

    def __setitem__(self, key, value):
        "Detect dictionary set events and emit change events."

        dict.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        "Detect dictionary del events and emit change events."

        dict.__delitem__(self, key)
        self.changed()


class CSV(TypeDecorator):
    impl = TEXT

    class Value(object):
        """Value type for fixture"""
        def __init__(self, val):
            self.val = val

        def __iter__(self):
            return self.val.__iter__()

    def process_bind_param(self, value, dialect):
        if value is None:
            return None

        # LIKE句を使っているところからも呼び出されるので...
        if isinstance(value, unicode) and (value.startswith(u'%') and value.endswith(u'%')):
            return value
        if isinstance(value, CSV.Value):
            value = value.val

        assert isinstance(value, list)
        return json.dumps(value, ensure_ascii=False, encoding='utf8')

    def process_result_value(self, value, dialect):
        if not value:
            return None
        rv = json.loads(value)
        assert isinstance(rv, list)

        # 空文字列が混入しているので消す
        # TODO: しばらくしたらこのコードは削除
        if u'' in rv:
            rv.remove(u'')

        return rv


class ProjectScopedQuery(Query):
    def get(self, ident):
        # override get() so that the flag is always checked in the
        # DB as opposed to pulling from the identity map. - this is optional.
        return Query.get(self.populate_existing(), ident)

    def __iter__(self):
        return Query.__iter__(self.private())

    def from_self(self, *ent):
        # override from_self() to automatically apply
        # the criterion too.   this works with count() and
        # others.
        return Query.from_self(self.private(), *ent)

    def private(self):
        mzero = self._mapper_zero()
        if mzero is not None:
            from listnr.community.views import current_project
            try:
                crit = mzero.class_.project_id == current_project.id
                return self.enable_assertions(False).filter(crit)
            except (AttributeError, RuntimeError), e:
                return self
        else:
            return self


def SecretColumn(*args, **kwargs):
    column = Column(*args, **kwargs)
    column.is_secret = True
    return column


def iterate_public_columns(model):
    for column in model.__table__.columns:
        if hasattr(column, 'is_secret') and column.is_secret:
            continue
        yield column


def printquery(statement, bind=None):
    """
    print a query, with values filled in
    for debugging purposes *only*
    for security, you should always separate queries from their values
    please also note that this function is quite slow
    """
    import sqlalchemy.orm
    if isinstance(statement, sqlalchemy.orm.Query):
        if bind is None:
            bind = statement.session.get_bind(
                    statement._mapper_zero_or_none()
            )
        statement = statement.statement
    elif bind is None:
        bind = statement.bind

    dialect = bind.dialect
    compiler = statement._compiler(dialect)

    class LiteralCompiler(compiler.__class__):
        def visit_bindparam(
                self, bindparam, within_columns_clause=False,
                literal_binds=False, **kwargs
        ):
            return super(LiteralCompiler, self).render_literal_bindparam(
                    bindparam, within_columns_clause=within_columns_clause,
                    literal_binds=literal_binds, **kwargs
            )

        def render_literal_value(self, value, type_):
            """Render the value of a bind parameter as a quoted literal.

            This is used for statement sections that do not accept bind paramters
            on the target driver/database.

            This should be implemented by subclasses using the quoting services
            of the DBAPI.

            """
            import datetime
            import decimal
            if isinstance(value, basestring):
                value = value.replace("'", "''")
                return "'%s'" % value
            elif value is None:
                return "NULL"
            elif isinstance(value, (float, int, long)):
                return repr(value)
            elif isinstance(value, decimal.Decimal):
                return str(value)
            elif isinstance(value, datetime.datetime):
                return value.strftime("'%Y-%m-%d %H:%M:%S'")

            else:
                raise NotImplementedError(
                            "Don't know how to literal-quote value %r" % value)  

    compiler = LiteralCompiler(dialect, statement)
    print compiler.process(statement)


# load all models
from .models import *
'''