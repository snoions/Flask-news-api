from flask import Flask
from flask.cli import with_appcontext
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import event
import json
import os
import mgflask


def _fk_pragma_on_connect(dbapi_con, con_record):
    # enables foreign key constraints for SQLite
    dbapi_con.execute('pragma foreign_keys=ON')

engine = create_engine('sqlite:///mgflask.db', convert_unicode=True)
event.listen(engine, 'connect', _fk_pragma_on_connect)


db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import mgflask.models
    Base.metadata.create_all(bind=engine)
    print('Created the database structure')
