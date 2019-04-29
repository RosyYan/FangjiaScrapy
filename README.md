# FangjiaScrapy
## 开发环境
| IDE | 数据库| 开发环境|python版本| 浏览器|
|-- | -- | -- | -- | -- |
|PyCharm| Mysql| conda| Python3.7| Chrome|
### 虚拟环境
```shell
# 创建虚拟环境，名为fangjia_scrapy
conda create -n fangjia_scrapy python=3
# 进入虚拟环境
activate fangjia_scrapy
# 离开环境
deactivate
```
### 相关库的安装
```shell
pip install scrapy
pip install mysqlclient
pip install pillow

# 反爬用到的库
pip install fake-useragent
pip install pytesseract
# 需要下载浏览器驱动：chromedriver
pip install selenium 

# 数据计算、分析库
pip install numpy
pip install pandas
pip install tensorflow

#数据可视化库
pip install matplotlib
pip install seaborn
pip install pyecharts
```

### 运行示例
`main.py`文件是项目运行的入口文件 

