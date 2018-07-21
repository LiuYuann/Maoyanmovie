import re
import os
import requests
from pyquery import PyQuery as pq
from fontTools import ttLib

URL = 'http://maoyan.com/films/1203528'

def enterPage():
    """
    请求页面
    :return: 页面pyquery对象
    """
    headers = {
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
    }
    response = requests.get(URL, headers=headers)
    doc = pq(response.text)
    return doc


def parseData(doc):
    """
    解析页面，获得数据
    :param doc: 页面pyquery对象
    :return: 原数据
    """
    codes = doc('.stonefont').items()
    data = []
    for code in codes:
        num = str(code.text().encode('unicode_escape').decode('utf8')).upper()
        num = num.split('\\U')
        data.append(num)
    return data


def getDict(doc):
    """
    获得数据解析字典
    :param doc: 页面pyquery对象
    :return: 数据解析字典
    """
    font_url = doc('style').text()
    font_url = re.sub("@font-face.*?format\('embedded-opentype'\),", '', font_url)
    font_url = 'http:' + re.search("(//vfile.meituan.net/colorstone.*?woff)", font_url).group(0)
    font2 = requests.get(font_url).content
    with open('2.woff', 'wb') as f:
        f.write(font2)
    font1 = ttLib.TTFont('1.woff')
    # 构建基准 {name: num}
    dict1 = {'glyph00000': ' ', 'x': '.', 'uniE29D': '9', 'uniF4B6': '6', 'uniE0A0': '1', 'uniEC40': '3',
             'uniE223': '5', 'uniF3C3': '2', 'uniE06A': '4', 'uniE48E': '0', 'uniF54D': '8', 'uniF705': '7'}
    font2 = ttLib.TTFont('2.woff')
    dict2 = {}
    for key in font2['glyf'].keys():
        for k, v in dict1.items():
            # 通过比较 字形定义 填充新的name和num映射关系
            if font1['glyf'][k] == font2['glyf'][key]:
                key = key.strip('uni')
                dict2[key] = v.lstrip()
                break
    os.remove('./2.woff')
    return dict2


def analyzeData(data, dict):
    """
    解析数据
    :param data: 原数据
    :param dict: 数据解析字典
    :return: 解析过的数据
    """
    value=[]
    for i in data:
        d = ''
        for j in i:
            for k, v in dict.items():
                if j.find(k) != -1:
                    d = d + v
                    if j.find('.') != -1:
                        d = d + '.'
                    break
        value.append(d)
    return value


def integrate(data, dict):
    """
    整合数据，返回最终数据
    :param data: 解析过的数据
    :param dict:
    :return:
    """
    d =analyzeData(data, dict)
    lengh = len(d)
    Data = {}
    if lengh == 1:
        Data['电影名'] = doc('.movie-brief-container > h3').text()
        Data['想看数'] = d[0]
    elif lengh == 2:
        Data['电影名'] = doc('.movie-brief-container > h3').text()
        Data['想看数'] = d[0]
        Data['累计票房'] = d[1] + doc('.unit').text()
    elif lengh == 3:
        Data['电影名'] = doc('.movie-brief-container > h3').text()
        Data['评分'] = d[0]
        Data['评价人数'] = d[1]
        Data['累计票房'] = d[2] + doc('.unit').text()
    else:
        print('程序内部错误')
    return Data


if __name__ == '__main__':
    doc = enterPage()
    dict = getDict(doc)
    data = parseData(doc)
    Data = integrate(data, dict)
    print(Data)
