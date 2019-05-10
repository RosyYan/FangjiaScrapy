# -*- coding: utf-8 -*-
__author__ = 'yzx'

import matplotlib.pyplot as plt
from pyecharts import Map, Pie, Line, Bar
import MySQLdb
import pandas as pd
from scipy.stats import norm
from pylab import mpl
import seaborn as sns

sns.set_style("whitegrid")
sns.set_style({'font.sans-serif': ['simhei', 'Arial']})
mpl.rcParams['font.sans-serif'] = ['SimHei']


class DataAnalysis(object):
    def __init__(self):
        self.conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="root123", db="house_spider", charset="utf8")
        self.cursor = self.conn.cursor()

    def run_sql(self, sql):
        results = []
        try:
            results = [i for i in self.cursor.fetchmany(self.cursor.execute(sql))]
            self.conn.commit()
        except Exception as e:
            print("sql exception:", e)
        return results

    def close(self):
        print('close resource.')
        self.cursor.close()
        self.conn.close()

    def get_data1(self, table_name):
        """
        二手房单价随时间变化
        """
        dates = []
        msg = []
        sql = """
            SELECT months, CAST(avg(unit_price) AS signed) from {0} where months >= '2018-12' and months<='2019-04' group by months ORDER BY months;
        """.format(table_name)

        data_list = self.run_sql(sql)
        for i, j in data_list:
            dates.append(i)
            msg.append(j)
        return dates, msg

    def draw_time_avg(self):
        """
        以折线图的形式展示二手房单价随时间的变化
        """
        line = Line('二手房均价(元)的变化')
        x, y1 = self.get_data1('v_fang')
        x, y2 = self.get_data1('v_lian')
        x, y3 = self.get_data1('v_anjuke')
        x, y4 = self.get_data1('v_yuan')
        line.add('房天下', x, y1, is_label_show=True)
        line.add('链家', x, y2, is_label_show=True)
        line.add('安居客', x, y3, is_label_show=True)
        line.add('阳光家缘', x, y4, is_label_show=True)
        line.render('./graphs/lines/line01.html')

    def handle(self, s):
        months, uprice = [], []
        datas = self.run_sql(s)
        for i, j in datas:
            months.append(i)
            uprice.append(j)
        return months, uprice

    def draw_time_area(self, web):
        """
        以折线图的形式展示各区的均价变化
        """
        fig, ax = plt.subplots(figsize=(8, 7))
        s = """
        SELECT months, CAST(avg(unit_price) AS signed) from {0} where months between '2018-12' and '2019-04' GROUP BY months ORDER BY months;
        """.format(web)
        x, y = self.handle(s)
        ax.plot(x, y, linewidth=1, marker='o', color='r', label='广州')
        # plt.style.use('ggplot')
        areas = []
        datas = self.run_sql('select distinct area from {0}'.format(web))
        for i in datas:
            areas.append(i[0])
        print(areas)
        colors = ['g', 'tan', 'gold', 'y', 'm', 'lightseagreen', 'purple', 'brown', 'teal', 'pink', 'chocolate', 'blue']
        for i in range(0, len(areas)):
            s = """
            SELECT months, CAST(avg(unit_price) AS signed) from {0} where area = '{1}' and months between '2018-12' and '2019-04' GROUP BY months ORDER BY months;
            """.format(web, areas[i])
            x, y = self.handle(s)
            ax.plot(x, y, linewidth=1, linestyle='--', marker='>', color=colors[i], label=areas[i])

        titles = {'v_lian': '链家', 'v_fang': '房天下', 'v_anjuke': '安居客', 'v_yuan': '阳光家缘'}
        # 设置x,y轴名称
        plt.xlabel("时间")
        plt.ylabel("元/㎡")
        plt.title(titles.get(web) + "各区二手房单价对比情况")
        # 显示网线
        plt.grid(True)

        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0)
        plt.savefig('./graphs/area.jpg', bbox_inches='tight')
        plt.show()

    def get_data2(self, tb):
        sql = """
        SELECT area, CAST(avg(unit_price) AS signed) avg_price from {0} GROUP BY area order by avg_price DESC;
        """.format(tb)
        result = self.run_sql(sql)
        areas = []
        per_price = []
        for i, j in result:
            areas.append(i)
            per_price.append(j)
        return areas, per_price

    def draw2(self):
        """
        以地图的形式展示各区的均价
        """
        names = ['链家', '房天下', '安居客', '阳光家缘']
        table = ['v_lian', 'v_fang', 'v_anjuke', 'v_yuan']
        for t in range(0, len(table)):
            areas, val = self.get_data2(table[t])
            map1 = Map(names[t] + "二手房均价(元)", width=1200, height=600)
            map1.add("均价", areas, val, maptype="广州", is_visualmap=True, visual_range=[min(val), max(val)],
                     visual_text_color="#000", is_map_symbol_show=False, is_label_show=True)
            map1.render(path='graphs/geos/' + names[t] + '.html')

    def get_data3(self, tb):
        sql = """select area, count(1) from {0} group by area""".format(tb)
        result = self.run_sql(sql)
        areas = []
        nums = []
        for i, j in result:
            areas.append(i)
            nums.append(j)
        return areas, nums

    def draw3(self):
        """
        以饼状图的形式展示各区二手房数量
        """
        names = ['链家', '房天下', '安居客', '阳光家缘']
        table = ['v_lian', 'v_fang', 'v_anjuke', 'v_yuan']
        for t in range(0, len(table)):
            areas, nums = self.get_data3(table[t])
            pie = Pie('各区二手房在售数量', names[t], title_pos='center', width=900)
            pie.add("数量", areas, nums, radius=[30, 60], label_text_color=None, is_label_show=True,
                    legend_orient='vertical', legend_pos='left')
            pie.render(path='graphs/pies/nums/' + names[t] + '.html')

    def draw_avg(self):
        """
        以柱状图的形式展示各网站的单价分布情况
        :return:
        """
        webs = ['链家', '房天下', '安居客', '阳光家缘']
        vals = []
        for item in ['v_lian', 'v_fang', 'v_anjuke', 'v_yuan']:
            x, y = self.get_data1(item)
            avg = 0
            for j in y:
                avg += j
            avg = int(avg / len(y))
            vals.append(avg)
        bar = Bar('二手房均价(元/平米)', '')
        bar.add("", webs, vals, is_label_show=True)
        bar.render('./graphs/bars/bar01.html')

        # 正态分布
        # x, y = self.get_data1('v_yuan')
        # a = [int(i) for i in y]
        # price = pd.Series(a, name="unit price")
        # ax = sns.distplot(price, fit=norm, kde=False)
        # plt.show()


if __name__ == '__main__':
    t = DataAnalysis()
    # 广州二手房单价走势图,以折线图形式展示
    # t.draw_time_avg()

    # 各区二手房单价走势图,以折线图形式展示
    for item in ['v_fang', 'v_lian', 'v_yuan', 'v_anjuke']:
        t.draw_time_area(item)

    # 各网站的均价对比图,以柱状图形式展示
    # t.draw_avg()

    # 各区二手房单价对比,以地图形式展示
    # t.draw2()

    # 各区二手房在售数量, 以饼图形式展示
    # t.draw3()
    # t.draw_area()
    t.close()
