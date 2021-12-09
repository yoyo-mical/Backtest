import pandas as pd
from inspect import getsource
import datetime
import pymysql
import requests
import tushare as ts
import datetime


pro = ts.pro_api()
today=datetime.date.today().strftime("%Y%m%d")
db_name = 'test'
conn = pymysql.connect(host='127.0.0.1', user='root', passwd='123456', db= db_name, charset='utf8',local_infile=1)
# conn.autocommit(1)
cur = conn.cursor()

sql1 = "select table_name from information_schema.tables where table_schema='{}'".format(db_name)
cur.execute(sql1)
result1 = cur.fetchall()
df1= pd.DataFrame(result1)
tabel_list = df1[0].to_list()

n = 0
for tabelname in tabel_list:
    sql2 = 'SELECT MAX(state_dt),stock_code FROM {} GROUP BY stock_code'.format(tabelname)
    cur.execute(sql2)
    result2 = cur.fetchall()
    df2 = pd.DataFrame(result2)
    df2[0]=df2[0].apply(lambda x: x+datetime.timedelta(days=1))
    df2[0]=df2[0].apply(lambda x: x.strftime("%Y%m%d"))
    df2[2]=df2.apply(tuple,axis=1)
    tulist = df2[2].to_list()

    i=0
    for tu in tulist:
        stdate = tu[0];tscode = tu[1]
        total = len(tulist)

        try:
            df = pro.daily(ts_code=tscode, start_date=stdate, end_date=today)
            # 打印进度
            strtip = 'Seq: ' + str(i + 1) + ' of ' + str(total) + '   Code: ' + str(tscode)
            print(strtip)
            c_len = df.shape[0]
        except Exception as aa:
            print(aa)
            print('No DATA Code: ' + str(i))
            continue
        for j in range(c_len):
            resu0 = list(df.iloc[c_len - 1 - j])
            resu = []
            for k in range(len(resu0)):
                if str(resu0[k]) == 'nan':
                    resu.append(-1)
                else:
                    resu.append(resu0[k])
            state_dt = (datetime.datetime.strptime(resu[1], "%Y%m%d")).strftime('%Y-%m-%d')
            try:
                sql_insert = "INSERT IGNORE INTO {} ".format(tabelname) + \
                             "(state_dt,stock_code,open,close,high,low,vol,amount,pre_close,amt_change,pct_change)" \
                             " VALUES ('%s', '%s', '%.2f', '%.2f','%.2f','%.2f','%i','%.2f','%.2f','%.2f','%.2f')" \
                             % (state_dt, str(resu[0]), float(resu[2]), float(resu[5]), float(resu[3]), float(resu[4]),
                                float(resu[9]), float(resu[10]), float(resu[6]), float(resu[7]), float(resu[8]))

                cur.execute(sql_insert)


            except Exception as err:
                continue

        i = i+1
        n = n + 1
        print(n,tscode,tabelname)
    conn.commit()

cur.close()
conn.close()

exit()








