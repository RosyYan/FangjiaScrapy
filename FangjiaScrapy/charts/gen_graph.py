# -*- coding: utf-8 -*-
__author__ = 'yzx'

import matplotlib.pyplot as plt
import MySQLdb
from pylab import mpl
import numpy as np
import seaborn as sns

sns.set_style({'font.sans-serif': ['simhei', 'Arial']})

mpl.rcParams['font.sans-serif'] = ['SimHei']
conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="root123", db="house_spider", charset="utf8")
cursor = conn.cursor()


def run_sql(sql):
    results = [i for i in cursor.fetchmany(cursor.execute(sql))]
    conn.commit()
    return results


def get_data(table_name, start_date):
    """
    广州二手房单价随时间变化
    :return: 时间，单价
    """
    dates = []
    msg = []
    sql = """
        SELECT DATE_FORMAT(sale_time,'%Y-%m') months, avg(unit_price) from {0} where sale_time >= '{1}' GROUP BY months ORDER BY months;
    """.format(table_name, start_date)

    data_list = run_sql(sql)
    conn.commit()
    for i, j in data_list:
        dates.append(i)
        msg.append(j)
    return dates, msg


def draw1():
    """
    对于各网站，广州二手房的平均价格随时间的走向
    :return:
    """
    plt.figure(1)
    x, y = get_data('anjuke', '2018-12-01')
    plt.plot(x, y, linewidth=1, marker='o', color='blue', label='安居客')

    x, y = get_data('fangtianxia', '2018-12-01')

    plt.plot(x, y, linewidth=1, marker='o', color='red', label='房天下')

    x, y = get_data('lianjia', '2018-12-01')
    plt.plot(x, y, linewidth=1, marker='o', color='green', label='链家')

    # 设置x,y轴名称
    plt.xlabel("时间")
    plt.ylabel("元/㎡")
    plt.title("广州二手房单价走向")
    # 显示网线
    plt.grid(linestyle='-.')
    plt.legend()
    plt.show()


def get_data2(tb):
    sql = """
    SELECT area, avg(unit_price) avg_price from {0} GROUP BY area order by avg_price DESC;
    """.format(tb)
    result = run_sql(sql)
    areas = []
    per_price = []
    for i, j in result:
        areas.append(i)
        per_price.append(j)
    return areas, per_price


def draw2():
    fig, [ax1, ax2, ax3] = plt.subplots(3, 1, figsize=(10, 8))
    x, y1 = get_data2('anjuke')
    sns.barplot(x, y1, palette='BuPu_r', ax=ax1)
    ax1.set_xlabel('安居客', fontsize=15)
    ax1.set_ylabel("元/㎡")
    ax1.set_title("广州各区二手房单价对比", fontsize=15)

    x, y2 = get_data2('lianjia')
    sns.barplot(x, y2, palette='Blues_d', ax=ax2)
    ax2.set_xlabel('链家', fontsize=15)
    ax2.set_ylabel("元/㎡")

    x, y3 = get_data2('fangtianxia')
    sns.barplot(x, y3, palette='Greens_d', ax=ax3)
    ax3.set_xlabel('房天下', fontsize=15)
    ax3.set_ylabel("元/㎡")

    sns.despine(bottom=True)
    # plt.savefig('./graphs/p1.jpg')
    plt.show()


if __name__ == '__main__':
    # draw1()  # 广州二手房的平均价格随时间的走向
    draw2()  # 广州各区二手房单价对比
    cursor.close()
    conn.close()
