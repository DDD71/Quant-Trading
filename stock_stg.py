'''
Author: 71
LastEditTime: 2022-03-30 22:00:57
version: 
Description: file content
'''
import akshare as ak
import mplfinance as mpf
import pandas as pd
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
from time import time
from tqdm import tqdm,trange
from basic import *


""" 函数速查表

stock_code = get_stock_code(stock_name)->str
stock_name = get_stock_name(stock_code)->str

plot_stock(stock_code,last_day=90)   

target_price,target_turnover = Stats_stock_min_trade(stock_code)

stock_candidate = find_red3soldier(up_rasing=3,qrr=3,leading_PE=50)


"""

now_time = datetime.now()

def Stats_stock_min_trade(stock_code,start_date=datetime.now().strftime("%Y%m%d"),end_date=datetime.now().strftime("%Y%m%d")):
    ''' 统计当日成交明细，按分钟计算，成交额/成交量作为价格
    input: stock_code : str
    output: target_price,target_turnover,stock_min_trade
    '''
    stock_min_trade = ak.stock_zh_a_hist_min_em(symbol=stock_code,start_date=start_date,end_date=end_date)
    if stock_min_trade.shape[0]<2:
        print('No data find !')
    data = {}
    for i in range(stock_min_trade.shape[0]):
        Turnover = stock_min_trade.loc[i,'成交量']
        stock_price = stock_min_trade.loc[i,'成交额']/Turnover/100
        stock_price = round(stock_price,2)
        if Turnover==0:
            continue
        if stock_price not in data.keys():
            data[stock_price] = Turnover
    target_price = list(data.keys())
    target_price.sort()
    target_turnover = [data[i] for i in target_price]
    # width= 0.01：股价个位数 , 0.05: 股价十位数 , 0.1: 股价百位数 , 千元股0.8
    if target_price[0]<10:
        width_set= 0.01
    elif target_price[0]<30:
        width_set= 0.02
    elif target_price[0]<100:
        width_set= 0.05
    elif target_price[0]<1000:
        width_set= 0.1
    else:
        width_set= 0.7
    plt.bar(target_price,height=target_turnover,width=width_set)
    print('Date:,',start_date)
    plt.title(get_stock_name(stock_code))
    plt.xlabel('price')
    plt.ylabel('Volume')
    return target_price,target_turnover

target_price,target_turnover = Stats_stock_min_trade(stock_code='002060')



def find_red3soldier(up_rasing=3,qrr=3,leading_PE=50):
    """ 找到最近一周 连续上涨的股票，红三兵形态,成交量放大,市盈率小于50
        input: up_rasing : int    当日最高涨幅
                qrr : int         当日量比
                leading_PE: int   动态市盈率
        output: stock_candidate ： list   备选股票
    """
    now_time = datetime.now()
    last_day7 = now_time - timedelta(days=7)
    stoch_today = ak.stock_zh_a_spot_em() # 当日股票
    stoch_today = stoch_today[stoch_today['代码'].str[0:2]!='68']  # 去除科创板
    stoch_today = stoch_today[stoch_today['代码'].str[0:2]!='30']  # 去除创业板
    stoch_today = stoch_today[stoch_today['代码'].str[0:1]!='4']  # 去除北京所
    stoch_today = stoch_today[stoch_today['代码'].str[0:1]!='8']  # 去除北京所
    stoch_today = stoch_today[stoch_today['涨跌幅']<up_rasing]  #当天红盘
    stoch_today = stoch_today[stoch_today['涨跌幅']>0]  #当天红盘
    stoch_today = stoch_today[stoch_today['量比']>qrr]  #当天红盘
    stoch_today = stoch_today.set_index('代码',drop=False)
    stock_candidate = []
    for stock_code in tqdm(stoch_today['代码']):
        stock_a_hist = ak.stock_zh_a_hist(symbol=stock_code,
                                    period='daily',
                                    start_date=last_day7.strftime("%Y%m%d"),
                                    end_date=now_time.strftime("%Y%m%d"))
        if stock_a_hist['涨跌幅'].iloc[-1]>0 and stock_a_hist['涨跌幅'].iloc[-2]>0 and stock_a_hist['涨跌幅'].iloc[-3]>0:
            if stock_a_hist['涨跌幅'].iloc[-2]<5 and stock_a_hist['涨跌幅'].iloc[-3]<5:
                if stock_a_hist['成交量'].iloc[-1]>stock_a_hist['成交量'].iloc[-2] and stock_a_hist['成交量'].iloc[-2] - stock_a_hist['成交量'].iloc[-3]:
                    if stoch_today.loc[stock_code]['市盈率-动态'] < leading_PE and stoch_today.loc[stock_code]['市盈率-动态']>0:
                        stock_candidate.append(stock_code)
    print(stock_candidate)
    return stock_candidate

