import pymysql.cursors
import pandas as pd
import datetime
import Recipe

# 寻找连续下跌stock,进行买卖回测；

# 生成时间序列：

state_dt = '2021-01-20'
para_window = 35
step = 5
date_seq ={}

date_start = (datetime.datetime.strptime(state_dt, '%Y-%m-%d')
              - datetime.timedelta(days=para_window)).strftime('%Y-%m-%d')
date_end = state_dt

db = pymysql.connect(host='127.0.0.1', user='root', passwd='123456', db='test', charset='utf8')
cursor = db.cursor()

sql_clear_recipe = "truncate TABLE deal_recipe"
cursor.execute(sql_clear_recipe)

sql_cal = "select state_dt from trade_cal where state_dt >= '{date_start}' and state_dt <= '{date_end}' " \
          "and is_open = 1 order by state_dt asc".format(date_start = date_start,date_end = date_end )

cursor.execute(sql_cal)
result_cal = cursor.fetchall()
df_cal = pd.DataFrame(result_cal)
date_temp = df_cal[0].to_list()

for x in range(0,len(date_temp),step+1):
    if x + step < len(date_temp):
        date_seq.update({date_temp[x].strftime('%Y-%m-%d'):date_temp[x+step].strftime('%Y-%m-%d')})
    else:
        break

db.commit()
db.close()
print(date_seq)


falllist = []

db_name = '科创板'

for date_buy,date_sell in date_seq.items():
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='123456', db=db_name, charset='utf8')
    cursor = db.cursor()

    sql1 = "select table_name from information_schema.tables where table_schema='{}'".format(db_name)
    cursor.execute(sql1)
    result1 = cursor.fetchall()
    df1 = pd.DataFrame(result1)
    tabel_list = df1[0].to_list()

    toplist = []

    for tb in tabel_list:
        sql2 = "select stock_code from {} group by stock_code".format(tb)
        cursor.execute(sql2)
        result2 = cursor.fetchall()
        df2 = pd.DataFrame(result2)
        codelist = df2[0].to_list()
        for code in codelist:
            n = 0
            try:
                sql3 = "select pct_change from {tb} where stock_code = '{code}' " \
                       "and state_dt< '{date_}'order by state_dt desc".format(tb=tb, code=code, date_=date_buy)
                cursor.execute(sql3)
                result3 = cursor.fetchall()
                df3 = pd.DataFrame(result3)
                pctlist = df3[0].to_list()
                for pct in pctlist:
                    if pct <= 0:
                        n = n + 1
                    else:
                        break
                tup = (tb, code, n)
                falllist.append(tup)
            except:
                print(tb, code)

    # print(falllist)
    df4 = pd.DataFrame(falllist)
    df4 = df4.sort_values(by=[2], ascending=False)
    print(df4)
    toplist = df4.iloc[0:9,1].to_list()
    datelist_buy = [date_buy]
    datelist_sell = [date_sell]
    stocklist = [toplist]
    moneylist = [[20000]]
    db.commit()
    db.close()
    Recipe.recipe_buy(datelist_buy,stocklist,moneylist,'equmoney_bycode')
    Recipe.recipe_sell(datelist_sell,stocklist)




