# -*- coding: utf-8 -*-
from flask import current_app
from sqlalchemy import *
from ..database import ModelBase


#db = current_app.db


class Ticker(ModelBase):
    __tablename__ = 'tickers'

    id = Column('ticker_id', Integer, primary_key=True)
    code = Column(String(255), unique=True, nullable=False)
    name = Column(Unicode(255), nullable=False, default=u'')
    is_active = Column(Boolean, nullable=False, default=True)
