import pymysql.cursors
import pandas as pd
import datetime
import backtrader as bt
import warnings
import builtins
import xlwings as xw


def excelshow(fpath,sheetname):
    app = xw.App(visible=True, add_book=False)
    app.display_alerts = False
    app.screen_updating = True
    wb = app.books.open(fpath)
    sht = wb.sheets(sheetname)
    sht.autofit()
    sht.range('A:Z').api.Font.Size = 10
    sht.range('A:Z').api.Font.Bold = False
    sht.range('A1:Z1').api.Font.Bold = True
    sht.range('A:Z').api.Font.Name = '微软雅黑'




filepath = r'D:\csvexcel\trade_list.csv'

try:
    wb = xw.Book(filepath)
    wb.app.kill()
except Exception as e:
    print(e)
    pass

dbname = '主板'
today = datetime.date.today().strftime('%Y-%m-%d')
perwin = 365
startdate = (datetime.datetime.strptime(today,'%Y-%m-%d')
             -datetime.timedelta(days=perwin)).strftime('%Y-%m-%d')

stock_tupe= ('601086.SH',)
# str_stock_tupe =
db = pymysql.connect(host='127.0.0.1',user='root',passwd='123456',db='test',charset='utf8' )
cursor = db.cursor()

if len(stock_tupe) == 1:
    sql_t = "select stock_code,industry from basic where stock_code in ('{}') ".format(stock_tupe[0])
else:
    sql_t = "select stock_code,industry from basic where stock_code in {} ".format(stock_tupe)

print(sql_t)

cursor.execute(sql_t)
result_t= cursor.fetchall()

db.commit()
db.close()
dic = {code:industry for code,industry in result_t}
print(dic)

# backtrader主体：
class MyStrategy(bt.Strategy):

    params = (('smaperiod',10),)

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('{},{}'.format(dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.trade_list = []

        self.sma = {x:bt.ind.MovingAverageSimple(self.getdatabyname(x),period= self.params.smaperiod)
                    for x in self.getdatanames()}

        # bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        # bt.indicators.WeightedMovingAverage(self.datas[0], period=25,
        #                                     subplot=True)
        # bt.indicators.StochasticSlow(self.datas[0])
        # bt.indicators.MACDHisto(self.datas[0])
        # rsi = bt.indicators.RSI(self.datas[0])
        # bt.indicators.SmoothedMovingAverage(rsi, period=10)
        # bt.indicators.ATR(self.datas[0], plot=False)

    def notify_order(self, order):
        '''使用这个函数，可以获取订单每次变动的信息，一般来说，使用固定的代码就行,下面是我自己在回测的时候，常用的固定代码'''

        if order.status in [order.Submitted, order.Accepted]:
            # order被提交和接受，这个一般不用打印出来，实盘的时候，可能少数情况下，需要测试这两个
            return
        if order.status == order.Rejected:
            self.log(f"order is rejected : order_ref:{order.ref}  order_info:{order.info}")
        if order.status == order.Margin:
            self.log(f"order need more margin : order_ref:{order.ref}  order_info:{order.info}")
        if order.status == order.Cancelled:
            self.log(f"order is concelled : order_ref:{order.ref}  order_info:{order.info}")
        if order.status == order.Partial:
            # 这个其实一般也只有在实盘中才会有，回测中，一般情况下，都是全部成交
            self.log(f"order is partial : order_ref:{order.ref}  order_info:{order.info}")
        # 如果订单完成了，就打印如下信息
        if order.status == order.Completed:
            if order.isbuy():

                self.trade_list.append((self.datas[0].datetime.date(0),order.p.data._name,
                                        self.broker.getvalue(), self.broker.getcash(), order.executed.pnl,
                                        order.executed.price, -order.executed.value,order.executed.comm,
                                        order.executed.size,'Buy'))
                pass

            else:
                self.trade_list.append((self.datas[0].datetime.date(0),order.p.data._name,
                                        self.broker.getvalue(), self.broker.getcash(), order.executed.pnl,
                                        order.executed.price, -order.executed.price*order.executed.size,
                                        order.executed.comm,order.executed.size,'Sell'))
                pass


    def next(self):

        for stock in stock_tupe:
            data_stock = self.getdatabyname(stock)
            # self.sma = bt.ind.MovingAverageSimple(data_stock, period=self.params.smaperiod)
            # print(self.sma[0])
            if self.getposition(data_stock).size <= 0:
                # print('buy',data_stock.datetime.date(1))

                if data_stock.close[0] < self.sma[stock]:
                    od = self.buy(size=50000)

            else:
                if data_stock.close[0] > self.sma[stock]:
                    # print('sell', data_stock.datetime.date(1))
                    od = self.close(data = data_stock)

    def stop(self):
        df = pd.DataFrame(self.trade_list, columns=['trade_date','stock_code',
                                                    'capital', 'cash', 'trade_pnl',
                                                    'trade_price', 'ordercost', 'trade_comm', 'vol', 'action'])

        df.to_csv(filepath, encoding='gbk')
        excelshow(filepath, 'trade_list')
        pass

if __name__ == '__main__':

    cerebro = bt.Cerebro()

    db = pymysql.connect(host='127.0.0.1', user='root', passwd='123456', db=dbname, charset='utf8')
    cursor = db.cursor()
    for stock_code,industry in dic.items():
        sql = "select state_dt,stock_code,open,high,low,close,vol from {tb} " \
              "where stock_code = '{code}' and state_dt between '{s}' and '{e}' " \
            .format(tb=industry, code=stock_code, s=startdate, e=today)
        cursor.execute(sql)
        result = cursor.fetchall()

        data = pd.DataFrame(result, columns=['Date', 'code', 'open', 'high', 'low', 'close', 'volume'])
        data['Date'] = pd.to_datetime(data['Date'])
        data.set_index('Date', inplace=True)

        brf_daily = bt.feeds.PandasData(dataname=data, fromdate=datetime.datetime.strptime(startdate, '%Y-%m-%d'),
                                        todate=datetime.datetime.strptime(today, '%Y-%m-%d'))

        cerebro.adddata(brf_daily,name=stock_code)

    db.commit()
    db.close()

        # print('{} Done'.format(stock))

    cerebro.addstrategy(MyStrategy)

    # broker配置
    starcash = 300000
    cerebro.broker.setcash(starcash)
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
    # cerebro.plot(style='candle')
    # cerebro.plot(volume=False)
    print("final capital is {:.2f},pnl is {:.2f};".format(cerebro.broker.getvalue(),
                                                           (cerebro.broker.getvalue()-starcash)/starcash))

exit()
