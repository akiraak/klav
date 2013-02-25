#! -*- coding:utf-8 -*-
import datetime
from sqlalchemy import *
from migrate import *
from klav.database import default_table_args
from flask import current_app


meta = MetaData()

tickers = Table(
    'tickers', meta,
    Column('ticker_id', Integer, primary_key=True),
    Column('code', String(255), unique=True, nullable=False),
    Column('name', Unicode(255), nullable=False, default=u''),
    Column('is_active', Boolean, nullable=False, default=True),
    **default_table_args
    )

market_records = Table(
    'market_records', meta,
    Column('market_record_id', Integer, primary_key=True),
    Column('ticker_id', Integer, ForeignKey('tickers.ticker_id'), nullable=False),
    Column('date', Date, nullable=False),
    Column('open_price', Integer, nullable=False),
    Column('close_price', Integer, nullable=False),
    Column('adj_close_price', Integer, nullable=False),
    Column('low_price', Integer, nullable=False),
    Column('high_price', Integer, nullable=False),
    Column('volume', Integer, nullable=False),
    **default_table_args
    )


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    tickers.create()
    market_records.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine

    tickers.drop()
    market_records.drop()
