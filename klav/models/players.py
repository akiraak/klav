# -*- coding: utf-8 -*-
from flask import current_app
from sqlalchemy import *
from sqlalchemy.orm import relationship, backref
from ..database import ModelBase


class Player(ModelBase):
    __tablename__ = 'players'

    id = Column('player_id', Integer, primary_key=True)
    name = Column(Unicode(255), nullable=False, default=u'')
    description = Column(Unicode(255), nullable=False, default=u'')
