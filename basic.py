import akshare as ak
import pandas as pd


def get_stock_code(stock_name)->str:
    '''输出股票名称得到股票代码
    input: stock_name : str 
    '''
    stock_list = ak.stock_zh_a_spot_em()
    stock_code = stock_list[stock_list['名称']==stock_name]['代码'].values[0]
    return stock_code


def get_stock_name(stock_code)->str:
    '''输出股票名称得到股票代码
    input: stock_code : str 
    '''
    stock_list = ak.stock_zh_a_spot_em()
    stock_name = stock_list[stock_list['代码']==stock_code]['名称'].values[0]
    return stock_name


def get_main_board_stock(stock_today=None):
    """
        默认返回当天A股所有股票,如输入stock_today则代表清晰创业板、北交所、新三板
        返回A股主板股票,删除创业板,北交所,新三板股票
    """
    if stock_today is None:
        stock_today = ak.stock_zh_a_spot_em() # 当日股票
    stock_today = stock_today[stock_today['代码'].str[0:2]!='68']  # 去除科创板
    stock_today = stock_today[stock_today['代码'].str[0:2]!='30']  # 去除创业板
    stock_today = stock_today[stock_today['代码'].str[0:1]!='4']  # 去除北京所，新三板
    stock_today = stock_today[stock_today['代码'].str[0:1]!='8']  # 去除新三板
    stock_today.sort_values(by='涨跌幅',ascending=False,inplace=True)
    return stock_today


def get_zt_stock(date):
    """
        获取涨停板
    """
    stock_today = ak.stock_em_zt_pool(date=date) 
    stock_today = get_main_board_stock(stock_today)
    stock_today.sort_values(by='连板数',ascending=False,inplace=True)
    return stock_today





