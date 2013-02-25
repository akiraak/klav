# -*- coding: utf-8 -*-
import datetime
from flask import current_app
from sqlalchemy import *
from sqlalchemy.orm import relationship, backref
from ..database import ModelBase
#from .tickers import Ticker


class UpdatedMarketRecord(ModelBase):
    __tablename__ = 'updated_market_records'

    id = Column('updated_market_record_id', Integer, primary_key=True)
    ticker_id = Column(Integer, ForeignKey('tickers.ticker_id'), nullable=False)
    date_updated = Column(Date, nullable=False)

    ticker = relationship('Ticker', backref=backref('updated_market_records', uselist=True, cascade='all, delete'))
