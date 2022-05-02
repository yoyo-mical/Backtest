# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import time
import pymysql.cursors
import pandas as pd
import datetime
import Recipe
import numpy as np

t1 = time.time()
N=20

df = pd.DataFrame({
    'A': pd.date_range(start='2021-01-01',periods=N,freq='D'),
    'x': np.linspace(0,stop=N-1,num=N),
    'y': np.random.rand(N),
    'C': np.random.choice(['Low','Medium','High'],N).tolist(),
    'D': np.random.normal(100, 10, size=(N)).tolist()
    })

for k in df.itertuples():
    print(k)
t2 = time.time()
b = time.ctime()
stuct1 = time.localtime(t2)
stuct2 = time.gmtime(t2)
print(stuct1)
print(stuct2)

exit()

def dbcon(db):
    def outter(func):
        def wrapper(text):
            conn = pymysql.connect(host='127.0.0.1', user='root', passwd='123456',
                                   db=db, charset='utf8',local_infile=1)
            cur = conn.cursor()

            func(text,cur)

            conn.commit()
            cur.close()
            conn.close()

        return wrapper
    return outter

db = 'test'

@dbcon(db)
def dbcontest(txt,cur):
    cur.execute(txt)
    result = cur.fetchall()
    df = pd.DataFrame(result,columns=['stock_code','name','industry'])
    print(df)

sql = "select stock_code,name,industry from basic where market = '主板'"
dbcontest(sql)


exit()



# conn = pymysql.connect(host='127.0.0.1', user='root', passwd='123456', db=db, charset='utf8', local_infile=1)
# cur = conn.cursor()
#
# sql = "select stock_code,name,industry from basic where market = '主板'"
# cur.execute(sql)
# result = cur.fetchall()
#
# df_stockname=pd.DataFrame(result,columns=['stock_code','name','industry'])
# # for (stock_code,name,industry) in result:
# #     # ind_code_dict.setdefault(industry,[]).append(stock_code)
#
# conn.commit()
# cur.close()
# conn.close()






l = [1,2,1,1]
t = (5,6,6,5)
d = {'a':9,'b':10,'c':11,'f':12}
s = {13,14,15,16}
st = 'gh,ky'

t1 = tuple(x for x in l)
t3 = tuple(x for x in d.values())
t4 = tuple(x for x in s)
l2 = [t1,t,t3,t4]
l3 = [x for x in d.keys()]
df = pd.DataFrame(l2,columns=l3,index=l3)
arr=np.array(l)
print([x for x in range(3)])


print(st.count('g'))
print(np.array(df.columns))
print(arr)


en=enumerate(st)
print(list(en))
print([i for i,x in en if x=='k'])

print(st.index('k'))

print(type(d.items()))

exit()

# def clocked(func):
#     t0 = time.perf_counter()
#     result = func()
#     elapsed = time.perf_counter() - t0
#     print (elapsed)
#     return result
#
# def clock(func):
#     def clocked(*args):
#         t0 = time.perf_counter()
#         result = func(*args)
#         elapsed = time.perf_counter() - t0
#         print (elapsed)
#         # return result
#     def clocked2(*args):
#         t0 = time.perf_counter()
#         result = func(*args)
#         elapsed = time.perf_counter() - t0+100
#         print(elapsed)
#
#     return clocked2
#
# def fclock(x):
#     def gclock(func):
#         def clock():
#             def clocked(*args):
#                 t0 = time.perf_counter()
#                 result = func(*args)
#                 elapsed = time.perf_counter() - t0
#                 print (elapsed)
#                 # return result
#             def clocked2(*args):
#                 t0 = time.perf_counter()
#                 result = func(*args)
#                 elapsed = time.perf_counter() - t0+x
#                 print(elapsed)
#
#             return clocked2
#         return clock
#     return gclock
#
# @fclock(1)
# def fact():
#     print('test')
#     return 1
#
# fact()
#
#
# # @clock
# # def fact():
# #     print('test')
# #     return 1
# #
# # f = fact()
# # # f = clocked(fact)
#
# exit()

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    a = 1+1
    print('PyCharm',a)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
