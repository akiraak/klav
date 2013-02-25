# -*- coding:utf-8 -*-
import os
import datetime
from flask.ext.script import Server, Manager, Command
#from flaskext.script import Manager, , prompt_bool, prompt_pass
from klav.application import create_app
from klav.database import db_session
from klav.models.tickers import Ticker
from klav.models.market_records import MarketRecord
from klav.models.updated_market_records import UpdatedMarketRecord


app = create_app('config.DevelopConfig')
db = app.db
manager = Manager(app)
manager.add_command("runserver", Server())

MARKET_RECORD_DATE_MIN = datetime.date(1990, 1, 1)


##### migrate command
class Migrate(Command):
    """SQLAlchemy-Migrateを動かす"""
    def create_parser(self, prog):
        class NullParser():
            def parse_args(self, args):
                class nullobject(object):
                    pass
                n = nullobject()
                n.args = args
                return n
        return NullParser()

    def run(self, args=[]):
        if args and args[0] == 'set_version':
            return self.set_version(args[1])

        from migrate.versioning.shell import main
        from flask import current_app

        repository = os.path.join(
            os.path.dirname(__file__),
            'schema')
        main(argv=args, debug=False,
             url=current_app.config['DATABASE_URI_ADMIN'],
             repository=repository,
             model='%s.database:ModelBase.metadata' % current_app.config['APP_TAG'],
             )

    def set_version(self, version):
        from listnr.database import raw_connect
        conn, opts = raw_connect(current_app, 'DATABASE_URI_ADMIN')
        curs = conn.cursor()
        curs.execute('UPDATE migrate_version SET version = ?', [int(version)])
        print 'ok'

manager.add_command('migrate', Migrate())


@manager.command
def init_tickers():
    from klav.tickers import tickers_info
    with db_session.begin():
        for info in tickers_info:
            ticker = Ticker.query.filter_by(code=info[0]).first()
            if not ticker:
                ticker = Ticker()
                db_session.add(ticker)
                print u'Add.    Code:%s Name:%s' % (info[0], info[1])
            else:
                print u'Update. Code:%s Name:%s' % (info[0], info[1])
            ticker.code = info[0]
            ticker.name = info[1]
            ticker.is_active = True


def update_market_records(start_date, end_date):
    from klav import kabu
    #now = datetime.datetime.now()
    #end_date = datetime.date(now.year, now.month, now.day)
    #start_date = datetime.date(now.year, now.month, 1)
    tickers = Ticker.query.filter_by(is_active=True).all()
    start_ticker_index = 192
    for i, ticker in enumerate(tickers):
        if i < start_ticker_index:
            continue
        try:
            # 株価の取得
            brand_name, stockpricess = kabu.getData(code=ticker.code, start_date=start_date, end_date=end_date)

            # 株価の表示
            print u'\n%d/%d 銘柄名:%s' % (i+1, len(tickers), brand_name)
            for sp in stockpricess:
                if 'open' in sp:
                    #print u'%d年%d月%d日 始値:%d 高値:%d 安値:%d 終値:%d 出来高:%s 調整後出来高:%s'%(sp['year'],sp['month'],sp['day'],sp['open'],sp['high'],sp['low'],sp['close'],sp['volume'],sp['adj_close'])
                    with db_session.begin():
                        date = datetime.date(sp['year'],sp['month'],sp['day'])
                        record = MarketRecord.query.filter_by(ticker_id=ticker.id).\
                            filter_by(date=date).first()
                        #print 'record:', record
                        if not record:
                            record = MarketRecord()
                            db_session.add(record)
                            #print u'Add.    ',
                        #else:
                        #    print u'Update. ',
                        #print u'%d年%d月%d日 始値:%d 高値:%d 安値:%d 終値:%d 出来高:%s 調整後出来高:%s'%(sp['year'],sp['month'],sp['day'],sp['open'],sp['high'],sp['low'],sp['close'],sp['volume'],sp['adj_close'])
                        record.ticker_id = ticker.id
                        record.date = date
                        record.open_price = sp['open']
                        record.close_price = sp['close']
                        record.adj_close_price = sp['adj_close']
                        record.low_price = sp['low']
                        record.high_price = sp['high']
                        record.volume = sp['volume']
                #else:
                #    print u'%d年%d月%d日 株分割等:%s'%(sp['year'],sp['month'],sp['day'],sp['comment'])
        except kabu.CodeError, e:
            print e


@manager.command
def update_market_records_this_month():
    now = datetime.datetime.now()
    start_date = datetime.date(now.year, now.month, 1)
    end_date = datetime.date(now.year, now.month, now.day)
    #start_date = datetime.date(2005, 3, 1)
    #end_date = datetime.date(2005, 3, 31)
    return update_market_records(start_date, end_date)


@manager.command
def update_market_records_since_1990():
    now = datetime.datetime.now()
    start_date = datetime.date(1990, 1, 1)
    end_date = datetime.date(now.year, now.month, now.day)
    return update_market_records(start_date, end_date)


@manager.command
def setup_updated_market_records():
    tickers = Ticker.query.all()
    for ticker in tickers:
        with db_session.begin():
            update = UpdatedMarketRecord.query.filter_by(ticker_id=ticker.id).first()
            if not update:
                update = UpdatedMarketRecord()
                update.ticker_id = ticker.id
                db_session.add(update)
            market_record = MarketRecord.query.filter_by(ticker_id=ticker.id).\
                order_by(MarketRecord.date.desc()).first()
            if market_record:
                update.date_updated = market_record.date
            else:
                update.date_updated = MARKET_RECORD_DATE_MIN
            print ticker.code, ticker.name, update.date_updated


@manager.command
def update_market_records():
    start_date = None
    end_date = datetime.date.today()
    last_update = UpdatMarketRecord.query.order_by(UpdatMarketRecord.date_update.desc()).first()
    if last_update:
        start_date = last_update.date_update + datetime.timedelta(days=1)
    else:
        start_date = datetime.date(1990, 1, 1)
    print 'start:', start_date
    print 'end  :', end_date
    #update_market_records(start_date, end_date)


@manager.command
def trade(ticker, start_date, end_date):
    records = MarketRecord.query.filter_by(ticker_id=ticker.id).\
        order_by(MarketRecord.date).all()
    first_money = 1000 * 10000
    money = first_money
    buy_value = 100
    stock_value = 0
    #for record in records:
    #    print record.date
    for record in records:
        if record.date.month % 2 == 0:
            if record.date.day == 25:
                money -= record.adj_close_price * buy_value
                stock_value = buy_value
                #print 'BUY :', record.date 
            if record.date.day == 10:
                money += record.adj_close_price * stock_value
                stock_value = 0
                #print 'SELL:', record.date, money
    print money - first_money, ticker.code, ticker.name


@manager.command
def trade_all():
    start_date = datetime.date(1980, 1, 1)
    end_date = datetime.date(2012, 8, 31)
    tickers = Ticker.query.filter_by(is_active=True).all()
    for i, ticker in enumerate(tickers):
        trade(ticker, start_date, end_date)
        #print i


@manager.command
def trade_month():
    ticker = Ticker.query.filter_by(is_active=True).first()
    start_year = 1980
    end_year = 2011
    records = MarketRecord.query.filter_by(ticker_id=ticker.id).\
        filter(MarketRecord.date >= datetime.date(start_year, 1, 1)).\
        filter(MarketRecord.date <= datetime.date(end_year, 12, 31)).\
        order_by(MarketRecord.date).all()
    for year in xrange(start_year, end_year + 1):
        print year


if __name__ == "__main__":
    manager.run()