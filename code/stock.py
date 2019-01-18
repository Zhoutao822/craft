# ==============================================================================
"""向log文件中定时写入数据模拟股票行情变化
版本：
    Python：3.6.7
数据来源网易财经，股票代码小米01810，源数据格式json，目标是解析json文件，获取data，
按照每分钟写入一次当前数据模拟股票行情的动态变化（实际上应该是获取秒级别的数据）
"""
import json
import time
import requests


def get_stock_data(market_code='hk', stock_code='01810'):
    """根据市场代码和股票代码获取json数据
    数据样例(日期，当前股价，平均股价，成交量):
    ['0930', 9.74, 9.74, 955918]
    ['0931', 9.73, 9.735, 259000]
    ['0932', 9.75, 9.74, 262600]
    ['0933', 9.69, 9.728, 563200]
    ['0934', 9.68, 9.718, 611200]
    Args:
        market_code: 市场代码，比如hs表示沪深，hk表示港股
        stock_code： 股票代码，比如港股的小米是01810
    Returns:
        data: 解析完成的数据list
    """
    url = ('http://img1.money.126.net/data/{}/time/today/{}.json').format(
        market_code, stock_code)
    # requests获取到的数据是byte类型，我们decode为utf-8
    response = requests.get(url)
    data = response.content.decode('utf-8')
    # decode后得到str类型数据，若满足条件：数组或对象之中的字符串必须使用双引号，
    # 不能使用单引号，则可以使用json.loads解析为json字典数据
    data = json.loads(data)
    return data['data']

def write2log(stock_data, file_path='./stock.log', delay=5):
    """将得到的list数据写入到.log文件中
    Args:
        stock_data: 解析得到的数据list
        file_path: log文件保存路径
        delay: 模拟的时间间隔 单位秒
    """
    for line in stock_data:
        line = [str(data) for data in line] # write写入数据为str类型
        line = ','.join(line) # 为了后续便于划分，这里使用逗号分隔
        print(line)
        with open(file_path, 'a+') as file:
            file.write(str(line) + '\n')
        time.sleep(delay)

if __name__ == "__main__":
    my_stock_data = get_stock_data('hk', '01810')
    write2log(my_stock_data)
