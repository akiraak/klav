#! -*- coding:utf-8 -*-
import datetime
from sqlalchemy import *
from migrate import *
from klav.database import default_table_args
from flask import current_app


meta = MetaData()

players = Table(
    'players', meta,
    Column('player_id', Integer, primary_key=True),
    Column('name', Unicode(255), nullable=False, default=u''),
    Column('description', Unicode(255), nullable=False, default=u''),
    **default_table_args
    )


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    players.create()
    

def downgrade(migrate_engine):
    meta.bind = migrate_engine

    players.drop()
