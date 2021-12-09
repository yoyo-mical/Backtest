import pymysql.cursors
import pandas as pd
import datetime
import backtrader as bt
import warnings
import builtins

# print(dir(bt.Strategy.stats))
# exit()

# 提取Datafeed
dbname1 = '主板'
db = pymysql.connect(host='127.0.0.1', user='root', passwd='123456', db=dbname1, charset='utf8')
cursor = db.cursor()
sql = "select state_dt,stock_code,open,high,low,close,vol from 元器件 " \
      "where stock_code = '000725.SZ' and state_dt <= '2021-12-03' and state_dt >= '2020-12-01' "
cursor.execute(sql)
result = cursor.fetchall()
data = pd.DataFrame(result)

db.commit()
db.close()

data.columns = ['Date', 'code', 'open', 'high', 'low', 'close', 'volume']
data['Date'] = pd.to_datetime(data['Date'])
data.set_index('Date', inplace=True)


# backtrader主体：
class MyStrategy(bt.Strategy):

    params = (('smaperiod',15),)

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('{},{}'.format(dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None

        self.sma = bt.ind.MovingAverageSimple(self.datas[0],period= self.params.smaperiod)
        # bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        # bt.indicators.WeightedMovingAverage(self.datas[0], period=25,
        #                                     subplot=True)
        # bt.indicators.StochasticSlow(self.datas[0])
        # bt.indicators.MACDHisto(self.datas[0])
        # rsi = bt.indicators.RSI(self.datas[0])
        # bt.indicators.SmoothedMovingAverage(rsi, period=10)
        # bt.indicators.ATR(self.datas[0], plot=False)



    def next(self):
        # if self.order:
        #     return
        if not self.position:
            if self.dataclose[0]<self.sma[0]:
                self.order = self.buy(size=10000)
        else:
            if self.dataclose[0] > self.sma[0]:
                self.order = self.close()


if __name__ == '__main__':

    cerebro = bt.Cerebro()


    brf_daily = bt.feeds.PandasData(dataname=data, fromdate=datetime.datetime(2020, 12, 3),
                                        todate=datetime.datetime(2021, 12, 3))
    cerebro.adddata(brf_daily)
        # print('{} Done'.format(stock))

    cerebro.addstrategy(MyStrategy)

    # broker配置
    cerebro.broker.setcash(200000)
    cerebro.broker.setcommission(commission=0.00025)
    cerebro.broker.set_slippage_perc(perc=0.0001)
    # print(cerebro.broker.get_value())
    # #
    # cerebro.addobserver(bt.observers.Broker)
    # cerebro.addobserver(bt.observers.Trades)
    # # cerebro.addobserver(bt.observers.BuySell)
    # cerebro.addobserver(bt.observers.TimeReturn)
    # cerebro.addobservermulti(bt.observers.Trades)

    # #添加策略分析模块；
    # cerebro.addanalyzer(bt.analyzers.TimeReturn,_name='pn1')
    # cerebro.addanalyzer(bt.analyzers.AnnualReturn,_name='_AnnualReturn')
    # cerebro.addanalyzer(bt.analyzers.SharpeRatio,_name='_SharpeRatio')
    # cerebro.addanalyzer(bt.analyzers.DrawDown,_name='_DrawDown')

    results = cerebro.run()
    # cerebro.plot()
    cerebro.plot(style='candle')
    # cerebro.plot(volume=False)

exit()
