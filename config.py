# -*- coding: utf-8 -*-


class ConfigBase(object):
    APP_TAG = 'klav'
    DEBUG = True
    DATABASE_URI_BASE = 'mysql+oursql://%s:%s@localhost/%s?charset=utf8mb4' % ('%s', '%s', APP_TAG)
    DATABASE_URI = DATABASE_URI_BASE % ('root', '')
    DATABASE_URI_ADMIN = DATABASE_URI_BASE % ('root', '')
    SQLALCHEMY_DATABASE_URI = DATABASE_URI_ADMIN


class DevelopConfig(ConfigBase):
    pass
