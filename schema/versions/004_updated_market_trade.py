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
    )

updated_market_records = Table(
    'updated_market_records', meta,

    Column('updated_market_record_id', Integer, primary_key=True),
    Column('ticker_id', Integer, ForeignKey('tickers.ticker_id'), nullable=False),
    Column('date_updated', Date, nullable=False),
    **default_table_args
    )


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    updated_market_records.create()
    

def downgrade(migrate_engine):
    meta.bind = migrate_engine

    updated_market_records.drop()
