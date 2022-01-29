import pandas as pd
import datetime
import pymysql
from collections import namedtuple
import xlwings as xw
import datetime
import numpy as np

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

filepath = r'D:\csvexcel\std.csv'

db = namedtuple('db','zb kc zx cy test')
log= namedtuple('log','stockcode' 'std')
ind_code_dict ={}
stdlist =[]
today = datetime.date.today().strftime('%Y-%m-%d')
startdate = today
datewindow = 365
enddate = (datetime.datetime.strptime(startdate,'%Y-%m-%d')-datetime.timedelta(days=datewindow)).strftime('%Y-%m-%d')
print(enddate)

db_name = db('主板','科创板','中小板','创业板','test')
print(type(db_name))
conn = pymysql.connect(host='127.0.0.1', user='root', passwd='123456', db=db_name.test, charset='utf8', local_infile=1)
cur = conn.cursor()

sql = "select stock_code,name,industry from basic where market = '主板'"
cur.execute(sql)
result = cur.fetchall()

df_stockname=pd.DataFrame(result,columns=['stock_code','name','industry'])
for (stock_code,name,industry) in result:
    ind_code_dict.setdefault(industry,[]).append(stock_code)

conn.commit()
cur.close()
conn.close()
print(ind_code_dict)

conn = pymysql.connect(host='127.0.0.1', user='root', passwd='123456', db=db_name.zb, charset='utf8', local_infile=1)
cur = conn.cursor()


for k,v in ind_code_dict.items():
    try:
        for code in v:
            sql1 = "select open,high,low,close from {tablename} where stock_code = '{code}' and " \
                   "state_dt between '{ed}' and '{sd}' order by state_dt desc" \
                .format(tablename=k,code =code,sd=startdate, ed=enddate)
            cur.execute(sql1)
            result1 = cur.fetchall()
            result1_ar = np.array(result1)
            result1_av = np.average(result1_ar)
            result1_std = np.std(result1_ar)
            result1_conpare  = result1_std/result1_av
            stdtuple = (code,result1_conpare)
            stdlist.append(stdtuple)
    except Exception as e:
        print(e)
        pass

conn.commit()
cur.close()
conn.close()

df_result = pd.DataFrame(stdlist,columns=['stock_code','标准差'])
df = pd.merge(df_result,df_stockname,on='stock_code')
df.sort_values(by='标准差',inplace=True)
df.to_csv(filepath,encoding="gbk")

excelshow(filepath,'std')

print(df)
exit()