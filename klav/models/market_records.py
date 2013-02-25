# -*- coding: utf-8 -*-
from flask import current_app
from sqlalchemy import *
from sqlalchemy.orm import relationship, backref
from ..database import ModelBase


class MarketRecord(ModelBase):
    __tablename__ = 'market_records'

    id = Column('market_record_id', Integer, primary_key=True)
    ticker_id = Column(Integer, ForeignKey('tickers.ticker_id'), nullable=False)
    date = Column(Date, nullable=False)
    open_price = Column(Integer, nullable=False)
    close_price = Column(Integer, nullable=False)
    adj_close_price = Column(Integer, nullable=False)
    low_price = Column(Integer, nullable=False)
    high_price = Column(Integer, nullable=False)
    volume = Column(Integer, nullable=False)

    UniqueConstraint('ticker_id', 'date')

    ticker = relationship('Ticker', backref=backref('market_records', uselist=True, cascade='all, delete'))
