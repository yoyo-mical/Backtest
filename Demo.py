import pymysql.cursors
import pandas as pd
import datetime
import backtrader as bt
import warnings
import builtins
import xlwings as xw
import collections

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
# 提取Datafeed
dbname1 = '科创板'
db = pymysql.connect(host='127.0.0.1', user='root', passwd='123456', db=dbname1, charset='utf8')
cursor = db.cursor()
sql = "select state_dt,stock_code,open,high,low,close,vol from 科创板 " \
      "where state_dt <= '2021-02-01' and state_dt >= '2020-12-01' "

# sql_t = "SELECT close FROM 科创板 WHERE stock_code IN ('688058.SH','688159.SH','688365.SH'," \
#         "'688218.SH','688360.SH','688228.SH','688020.SH','688518.SH','688156.SH') and state_dt = '2021-01-25' "
#
# cursor.execute(sql_t)
# result_t = cursor.fetchall()
# list_t = [x[0]*100 for x in result_t]
# sumt =sum(list_t,68349)



cursor.execute(sql)
result = cursor.fetchall()
data = pd.DataFrame(result,columns = ['Date', 'code', 'open', 'high', 'low', 'close', 'volume'])



db.commit()
db.close()

# pd.set_option('display.max_rows',None)
# print(data[1])

dbname2 = 'test'
db = pymysql.connect(host='127.0.0.1', user='root', passwd='123456', db=dbname2, charset='utf8')
cursor = db.cursor()
sql = "select stock_code from deal_recipe group by stock_code"
sql_all = "select * from deal_recipe where action = 'buy'"
cursor.execute(sql)
result2 = cursor.fetchall()
stocklist = [x[0] for x in result2]
cursor.execute(sql_all)
result3 = cursor.fetchall()
trade_info = pd.DataFrame(result3,columns = ['action', 'stock_dt', 'sec_code', 'vol'])
db.commit()
db.close()

orderinfo = collections.namedtuple('orderinfo','ref stockname')
# backtrader主体：
class MyStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('{},{}'.format(dt.isoformat(), txt))

    def __init__(self):
        self.buy_stock = trade_info
        self.trade_dates = pd.to_datetime(self.buy_stock['stock_dt'].unique()).to_list()
        self.sellorder_list = []
        self.buyorder_list = []
        self.buy_stock_pre = []
        self.trade_list = []


    # def notify_cashvalue(self, cash, value):
    #     print("现有总资产是{}，现有资金是{}".format(value, cash))

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
            self.ord = order
            # 如果是做多或者平空
            if order.isbuy():
                self.trade_list.append((self.datas[0].datetime.date(0), order.p.data._name,
                                        self.broker.getvalue(), self.broker.getcash(), order.executed.pnl,
                                        order.executed.price, -order.executed.value,order.executed.comm,
                                        order.executed.size,'Buy'))
                # self.log("buy result : buy_price : {} , buy_cost : {} , commission : {}"
                #                  .format(order.executed.price, order.executed.value, order.executed.comm))
            # 如果是平多或者做空
            else:
                self.trade_list.append((self.datas[0].datetime.date(0), order.p.data._name,
                                        self.broker.getvalue(), self.broker.getcash(), order.executed.pnl,
                                        order.executed.price, -order.executed.price*order.executed.size,
                                        order.executed.comm,order.executed.size,'Sell'))
                # self.log("sell result : sell_price : {} , sell_cost : {} , commission : {}"
                #          .format(order.executed.price, order.executed.value, order.executed.comm))

    def notify_trade(self, trade):
        '''这个函数可以获取每次交易的变动信息'''
        # 一个trade结束的时候输出信息
        self.trade = trade
        # if trade.isclosed:
        #     self.log('closed symbol is : {} , total_profit : {} , net_profit : {}'.format(
        #         trade.getdataname(), trade.pnl, trade.pnlcomm))
        # # trade开始的时候输入的信息
        # if trade.isopen:
        #     self.log('open symbol is : {} , price : {} '.format(
        #         trade.getdataname(), trade.price))
    #     # 如果想要把每笔交易都输出出来，可以在init中，设置self.trade_result=[],这样，
    #     # 把每笔交易的开和平，都保存在这里面，在stop中输出到本地进行校对策略。
    #     # self.trade_list.append([self.datas[0].datetime.date(0), self.stats.broker.value[0], self.stats.broker.cash[0],
    #     #                         trade.getdataname(), trade.size, self.getdatabyname(trade.getdataname()).open[0],
    #     #                         trade.data.open[-1 * trade.barlen], trade.pnl, trade.pnlcomm])
    #
    #     self.trade_list.append((self.datas[0].datetime.date(0), trade.getdataname(),self.stats.broker.value[0], self.stats.broker.cash[0],
    #                               trade.pnl, trade.price,trade.size))


    def next(self):
        dt = self.datas[0].datetime.date(0)
        # print(self.stats.broker.value[0])
        if dt in self.trade_dates:
            self.buyorder_list = []
            self.sellorder_list = []
            print(f"----------------------------{dt}为调仓日----------------------------")
            # if len(self.order_list) > 0:
            #     print('od>0')
            #     for od in self.order_list:
            #         self.cancel(od)
            #     self.order_list = []
            buy_stocks_data = self.buy_stock.query(f"stock_dt=='{dt}'")
            long_list = buy_stocks_data['sec_code'].to_list()
            print('long_list', dt, long_list)
            sell_stock = [i for i in self.buy_stock_pre if i not in long_list]
            print('sell_stock', sell_stock)
            if len(sell_stock) > 0:
                print('对不在持有的股票进行平仓----------')
                for stock in sell_stock:
                    data_stock = self.getdatabyname(stock)
                    if self.getposition(data_stock).size > 0:
                        # print('{}，持仓量是{}，持仓价格是{}'.format(stock, self.getposition(data_stock).size,
                        #                                  self.getposition(data_stock).price))
                        od = self.close(data=data_stock)
                        sellorder = orderinfo(od.ref,stock)
                        self.sellorder_list.append(sellorder)
            print("买入此次调仓期的股票----------")
            for stock in long_list:
                data_stock = self.getdatabyname(stock)
                od = self.buy(data=data_stock, size=100)
                buyorder = orderinfo(od.ref, stock)
                self.buyorder_list.append(buyorder)

            self.buy_stock_pre = long_list


    def stop(self):
        # pd.set_option('display.max_rows', None)
        # pd.set_option('display.max_columns', None)

        df = pd.DataFrame(self.trade_list,columns=['trade_date','stock_code',
                                                   'capital','cash','trade_pnl',
                                                   'trade_price','ordercost','trade_comm','vol','action'])

        # df_order = pd.DataFrame(dir(self.ord.p),columns=['order'])
        # dr_order_executed = pd.DataFrame(dir(self.ord.executed),columns=['order.executed'])
        # dr_trade = pd.DataFrame(dir(self.trade), columns=['trade'])
        # df = pd.concat([df_order,dr_order_executed,dr_trade],axis=1)

        df.to_csv(filepath,encoding='gbk')
        excelshow(filepath, 'trade_list')
        pass


if __name__ == '__main__':

    cerebro = bt.Cerebro(stdstats=False)

    group = data.groupby('code')
    for stock in stocklist:
        df = group.get_group(stock)[['Date', 'open', 'high', 'low', 'close', 'volume']]
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        brf_daily = bt.feeds.PandasData(dataname=df, fromdate=datetime.datetime(2020, 12, 10),
                                        todate=datetime.datetime(2021, 1, 25), plot=False)
        cerebro.adddata(brf_daily, name=stock)
        # print('{} Done'.format(stock))

    cerebro.addstrategy(MyStrategy)

    # broker配置
    cerebro.broker.setcash(100000)
    cerebro.broker.setcommission(commission=0.00025)
    cerebro.broker.set_slippage_perc(perc=0.0001)
    print(cerebro.broker.get_value())
    #
    cerebro.addobserver(bt.observers.Broker)
    cerebro.addobserver(bt.observers.Trades)
    # cerebro.addobserver(bt.observers.BuySell)
    cerebro.addobserver(bt.observers.TimeReturn)
    # cerebro.addobservermulti(bt.observers.Trades)

    # #添加策略分析模块；
    # cerebro.addanalyzer(bt.analyzers.TimeReturn,_name='pn1')
    # cerebro.addanalyzer(bt.analyzers.AnnualReturn,_name='_AnnualReturn')
    # cerebro.addanalyzer(bt.analyzers.SharpeRatio,_name='_SharpeRatio')
    # cerebro.addanalyzer(bt.analyzers.DrawDown,_name='_DrawDown')

    results = cerebro.run()

    # cerebro.plot(style='candle')
    # cerebro.plot(volume=False)
    print("final capital is {:.2f},cash is {:.2f};".format(cerebro.broker.getvalue(),cerebro.broker.getcash()))

exit()
