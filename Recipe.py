import pymysql

def recipe_buy(datelist, codelist, moneylist, buymark):
    buyactlist = []
    if len(datelist) != len(codelist):
        print('datalist与codelist 长度不匹配')
        return 0

    elif len(moneylist) != len(codelist):
        print('moneylist与codelist 长度不匹配')
        return 0

    db = pymysql.connect(host='127.0.0.1', user='root', passwd='123456', db='test', charset='utf8')
    cursor = db.cursor()

    if buymark == 'equmoney_bycode':
        for i in range(len(datelist)):
            for j in range(len(codelist[i])):
                sql_recipe = "insert ignore into deal_recipe (action,state_dt,stock_code,money)" \
                             "value ('{}','{}','{}',{})" \
                    .format('buy', datelist[i], codelist[i][j], moneylist[i][0])
                cursor.execute(sql_recipe)
                tup_buy = ('buy', datelist[i], codelist[i][j], moneylist[i][0])
                buyactlist.append(tup_buy)
    elif buymark == 'defmoney_bycode':
        for i in range(len(datelist)):
            for j in range(len(codelist[i])):
                sql_recipe = "insert ignore into deal_recipe (action,state_dt,stock_code,money)" \
                             "value ('{}','{}','{}',{})" \
                    .format('buy', datelist[i], codelist[i][j], moneylist[i][j])
                cursor.execute(sql_recipe)
                tup_buy = ('buy', datelist[i], codelist[i][j], moneylist[i][j])
                buyactlist.append(tup_buy)

    db.commit()
    db.close()
    return buyactlist

def recipe_sell(datelist, codelist):
    sellactlist = []
    if len(datelist) != len(codelist):
        print('datalist与codelist 长度不匹配')
        return 0
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='123456', db='test', charset='utf8')
    cursor = db.cursor()

    for i in range(len(datelist)):
        for j in range(len(codelist[i])):
            sql_recipe = "insert ignore into deal_recipe (action,state_dt,stock_code)" \
                         "value ('{}','{}','{}')" \
                .format('sell', datelist[i], codelist[i][j])
            cursor.execute(sql_recipe)
            tup_sell = ('sell', datelist[i], codelist[i][j])
            sellactlist.append(tup_sell)

    db.commit()
    db.close()
    return sellactlist


