# -*- coding: utf-8 -*-
__author__ = 'yzx'

import matplotlib.pyplot as plt
import MySQLdb
from pylab import mpl
import seaborn as sns
from urllib.request import quote, urlopen
import json
import traceback

sns.set_style("whitegrid")
sns.set_style({'font.sans-serif': ['simhei', 'Arial']})
mpl.rcParams['font.sans-serif'] = ['SimHei']


class DataAnalysis(object):
    def __init__(self):
        self.conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="root123", db="house_spider", charset="utf8")
        self.cursor = self.conn.cursor()

    def run_sql(self, sql):
        results = [i for i in self.cursor.fetchmany(self.cursor.execute(sql))]
        self.conn.commit()
        return results

    def close(self):
        print('close resource.')
        self.cursor.close()
        self.conn.close()

    def get_data1(self, table_name, start_date):
        """
        广州二手房单价随时间变化
        :return: 时间，单价
        """
        dates = []
        msg = []
        sql = """
            SELECT DATE_FORMAT(sale_time,'%Y-%m') months, avg(unit_price) from {0} where sale_time >= '{1}' and sale_time<'2019-04-01' GROUP BY months ORDER BY months;
        """.format(table_name, start_date)

        data_list = self.run_sql(sql)
        for i, j in data_list:
            dates.append(i)
            msg.append(j)
        return dates, msg

    def draw1(self):
        """
        广州近月二手房单价走势图
        :return:
        """
        x, y = self.get_data1('fangtianxia', '2018-12-01')
        print("fang:"+ y)

        plt.plot(x, y, linewidth=1, marker='o', color='red', label='房天下')

        x, y = self.get_data1('lianjia', '2018-12-01')
        plt.plot(x, y, linewidth=1, marker='o', color='green', label='链家')

        x, y = self.get_data1('jiayuan', '2018-12-01')
        plt.plot(x, y, linewidth=1, marker='o', color='purple', label='阳光家缘')

        # 设置x,y轴名称
        plt.xlabel("时间")
        plt.ylabel("元/㎡")
        plt.title("广州二手房单价图")
        # 显示网线
        plt.grid(linestyle='-.')
        plt.legend()
        plt.savefig('./graphs/p1.jpg')
        plt.show()

    def get_data2(self, tb):
        sql = """
        SELECT area, avg(unit_price) avg_price from {0} GROUP BY area order by avg_price DESC;
        """.format(tb)
        result = self.run_sql(sql)
        areas = []
        per_price = []
        for i, j in result:
            areas.append(i)
            per_price.append(j)
        return areas, per_price

    def draw2(self):
        fig, [ax1, ax2, ax3] = plt.subplots(3, 1, figsize=(14, 15))
        x, y1 = self.get_data2('v_lian')
        sns.barplot(x, y1, palette='BuPu_d', ax=ax1)

        ax1.set_xlabel('链家', fontsize=14)
        ax1.set_ylabel("元/㎡")
        ax1.set_title("广州不同区域二手房单价对比", fontsize=16)

        x, y2 = self.get_data2('v_fang')
        sns.barplot(x, y2, palette='Greens_d', ax=ax2)
        ax2.set_xlabel('房天下', fontsize=14)
        ax2.set_ylabel("元/㎡")

        x, y3 = self.get_data2('v_yuan')
        sns.barplot(x, y3, palette='Blues_d', ax=ax3)
        ax3.set_xlabel('阳光家缘', fontsize=14)
        ax3.set_ylabel("元/㎡")

        sns.despine(bottom=True)
        plt.savefig('./graphs/p2.jpg')
        plt.show()

    def get_data3(self, tb):
        '''
        各区二手房数量
        '''
        sql = """select area, count(1) from {0} group by area""".format(tb)
        result = self.run_sql(sql)
        areas = []
        per_price = []
        for i, j in result:
            areas.append(i)
            per_price.append(j)
        return areas, per_price

    def draw3(self):
        fig, [ax1, ax2, ax3] = plt.subplots(3, 1, figsize=(12, 14))
        x, y1 = self.get_data3('v_lian')
        sns.barplot(x, y1, palette='BuPu_d', ax=ax1)

        ax1.set_xlabel('链家', fontsize=14)
        ax1.set_ylabel("元/㎡")
        ax1.set_title("广州各区二手房数量", fontsize=16)

        x, y2 = self.get_data3('v_fang')
        sns.barplot(x, y2, palette='Greens_d', ax=ax2)
        ax2.set_xlabel('房天下', fontsize=14)
        ax2.set_ylabel("元/㎡")

        x, y3 = self.get_data3('v_yuan')
        sns.barplot(x, y3, palette='Blues_d', ax=ax3)
        ax3.set_xlabel('阳光家缘', fontsize=14)
        ax3.set_ylabel("元/㎡")

        sns.despine(bottom=True)
        plt.savefig('./graphs/p3.jpg')
        plt.show()

    def getlnglat(self, address):
        """
        调用百度地图API获取广州各区的经纬度
        """
        url = 'http://api.map.baidu.com/geocoder/v2/?address='
        output = 'json'
        ak = 'eytjjeq53la0ZFxpXuAKL0MYBDb3c7S3'
        add = quote(address)
        req = urlopen(url + add + '&output=' + output + '&ak=' + ak)
        res = req.read().decode()
        return json.loads(res)

    def save_points(self, website):
        """
        保存website在date月份的points
        :return:
        """
        uri = 'points/' + website + '.json'
        file = open(uri, 'w')
        dates = ['2018-12', '2019-01', '2019-02', '2019-03']
        points_dict = dict()
        for i in dates:
            sql = """
            SELECT area,FlOOR(avg(unit_price)) avg_price from {0}  where sale_month = '{1}' GROUP BY area,sale_month
            """.format(website, i)
            arr = []
            datas = self.run_sql(sql)
            for area, price in datas:
                lng = self.getlnglat(area)['result']['location']['lng']  # 经度
                lat = self.getlnglat(area)['result']['location']['lat']  # 维度
                tmp = {"lng": str(lng), "lat": str(lat), "count": str(price)}
                arr.append(tmp)
            points_dict.update({i: arr})
        try:
            file.write(json.dumps(points_dict))
        except:
            f = open('./error.txt', 'a')
            traceback.print_exc(file=f)
            f.flush()
        file.close()


if __name__ == '__main__':
    t = DataAnalysis()
    # t.save_points('v_anjuke')
    #  广州近月二手房单价走势图
    # t.draw1()
    #  广州不同区域二手房单价对比
    # t.draw2()
    t.draw3()
    t.close()
