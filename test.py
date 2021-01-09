from pyecharts.charts import Bar
from xlsx2csv import Xlsx2csv
import sqlite3

import myda.dbutils

# bar = Bar().add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"]).add_yaxis("商家A", [5, 20, 36, 10, 75, 90])



if __name__=='__main__':

    # bar.render()
    # Xlsx2csv("仪器数据.xlsx", outputencoding="utf-8").convert("test.csv")

    # myda.dbutils.create_db()
    # myda.dbutils.create_table()

    # address = [('海门',121.15,31.89),('鄂尔多斯',109.781327, 39.608266)]
    # myda.dbutils.update_geo(address)
    # conn = sqlite3.connect('geo.db')
    myda.dbutils.create_db()
    myda.dbutils.create_table()


    # cursor = conn.execute(
    #     "SELECT id, name, lng, lat  from geo")
    #
    # for row in cursor:
    #     print("ID = ", row[0])
    #     print("NAME = ", row[1])
    #     print("lng = ", row[2])
    #     print("lat = ", row[3],
    #           "\n")

    # print(myda.dbutils.select_geo(('海门', '鄂尔多斯')))







