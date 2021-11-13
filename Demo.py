import pymysql.cursors
import pandas as pd
import datetime
import backtrader as bt
import warnings
import builtins

dbname = '主板'

db = pymysql.connect(host='127.0.0.1', user='root', passwd='123456', db= dbname, charset='utf8')
cursor = db.cursor()
sql = "select state_dt,open,high,low,close,vol from it设备 " \
      "where stock_code ='000021.SZ' and state_dt <= '2021-09-24' and state_dt >= '2020-05-24' "
cursor.execute(sql)
result = cursor.fetchall()

data = pd.DataFrame(result)

db.commit()
db.close()

data.columns=['Date','open','high','low','close','volume']
data['Date']=data['Date'].apply(lambda x:datetime.datetime.strftime(x,'%Y/%m/%d'))
data['Date'] = pd.to_datetime(data['Date'])
data.set_index('Date',inplace=True)
# data['openinterest'] = 0
# print(data)

class MyStrategy(bt.Strategy):

    def log(self,txt,dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('{},{}'.format(dt.isoformat(),txt))

    def __init__(self):
        self.dataclose = self.datas[0].close

    def next(self):
        self.log('Close,{}'.format(self.dataclose[0]))

if __name__ == '__main__':

    cerebro = bt.Cerebro()

    brf_daily = bt.feeds.PandasData(dataname=data,fromdate=datetime.datetime(2020, 7, 22),
                                    todate = datetime.datetime(2021,8,16))

    cerebro.addstrategy(MyStrategy)

    cerebro.adddata(brf_daily)

    cerebro.broker.setcash(100000)

    cerebro.run()

exit()

#

# cerebro = bt.Cerebro()
#
# print(brf_daily)
#
# cerebro.adddata(brf_daily)
#
# cerebro.addstrategy(MyStrategy)
#
# cerebro.run()
#
# cerebro.plot(style='candle')
