#! -*- coding:utf-8 -*-
import datetime
from sqlalchemy import *
from migrate import *
from klav.database import default_table_args
from flask import current_app
from klav.models.trades import TradeType


meta = MetaData()

players = Table(
    'players', meta,
    Column('player_id', Integer, primary_key=True),
    )

market_records = Table(
    'market_records', meta,
    Column('market_record_id', Integer, primary_key=True),
    )

trades = Table(
    'trades', meta,
    Column('player_id', Integer, ForeignKey('players.player_id'), nullable=False),
    Column('market_record_id', Integer, ForeignKey('market_records.market_record_id'), nullable=False),
    Column('trade_type', Enum(TradeType.BUY, TradeType.SELL, name='trade_type'), nullable=False),
    **default_table_args
    )


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    trades.create()
    

def downgrade(migrate_engine):
    meta.bind = migrate_engine

    trades.drop()
