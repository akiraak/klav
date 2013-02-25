# -*- coding: utf-8 -*-
from flask import current_app
from sqlalchemy import *
from sqlalchemy.orm import relationship, backref
from ..database import ModelBase


class TradeType(object):
    BUY = 'buy'
    SELL = 'sell'
    VALUES = [BUY, SELL]


class Trade(ModelBase):
    __tablename__ = 'trades'

    id = Column('trade_id', Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.player_id'), nullable=False)
    market_record_id = Column(Integer, ForeignKey('market_records.market_record_id'), nullable=False)
    trade_type = Column(Enum(*TradeType.VALUES, name='trade_type'), nullable=False)

    player = relationship('Player', backref=backref('tradess', uselist=True, cascade='all, delete'))
    market_record = relationship('MarketRecord', backref=backref('tradess', uselist=True, cascade='all, delete'))
