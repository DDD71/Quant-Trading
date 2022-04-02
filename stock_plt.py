import akshare as ak
import mplfinance as mpf
import pandas as pd
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
from time import time
from tqdm import tqdm,trange
from basic import *

from typing import List, Union
from pyecharts import options as opts
from pyecharts.charts import Kline, Line, Bar, Grid


 

def plot_stock_mpf(stock_code,last_day=90):
    '''绘制股票K线图，默认日线90天
    input: stock_code : str
            ast_day : int  
    ouput: None
    '''
    mc = mpf.make_marketcolors(
    up="red",  # 上涨K线的颜色
    down="green",  # 下跌K线的颜色
    edge="inherit",  # 蜡烛图箱体的颜色
    volume="inherit",  # 成交量柱子的颜色
    wick="inherit")  # 蜡烛图影线的颜色
    # 调用make_mpf_style函数，自定义图表样式
    # 函数返回一个字典，查看字典包含的数据，按照需求和规范调整参数
    selfstyle = mpf.make_mpf_style(base_mpl_style="ggplot", marketcolors=mc)
    now_time = datetime.now()
    lastday = now_time - timedelta(days=last_day)
    df = ak.stock_zh_a_hist(symbol=stock_code,adjust="qfq")
    df['日期'] = pd.to_datetime(df['日期'])
    df = df.set_index('日期')
    df = df[["开盘", "最高", "最低", "收盘", "成交量"]]
    df.columns = ["Open", "High", "Low", "Close", "Volume"]
    df.index.name = "Date"
    df = df[lastday.strftime("%Y%m%d"):now_time.strftime("%Y%m%d")]
    mpf.plot(df,style=selfstyle,type='candle',mav=(5,11,21),figratio=(16,9),volume=True,show_nontrading=False,title=get_stock_name(stock_code))

   
def plot_stocks(stocks:list):
    """连续绘制K线图
        stocks->list
    """
    for code in stocks:
        plot_stock(code,last_day=90)
        if code != stocks[-1]:
            plt.waitforbuttonpress()



def get_stock_data(stock_code,last_day=90):
    ''' 获取股票数据
    input: stock_code : str
            last_day : int  
    return: list
    '''
    df = ak.stock_zh_a_hist(symbol=stock_code,adjust="qfq")
    df = df[['日期',"开盘","收盘","最低","最高","成交量"]]  # 注意顺序
    df['日期'] = pd.to_datetime(df['日期'])
    df = df.set_index('日期',drop=False)
    now_time = datetime.now()
    lastday = now_time - timedelta(days=last_day)
    df = df[lastday.strftime("%Y%m%d"):now_time.strftime("%Y%m%d")]
    return df.values.tolist()

def split_data(data:list)->dict: 
    """" 数据格式切分。
        返回数据：data
        {'日期': ,
         '价格': ,
         '成交量':[number,volumes,涨跌flag] }
    """
    category_data = []
    values = []
    volumes = []

    for i, tick in enumerate(data):
        category_data.append(tick[0])
        values.append(tick)
        volumes.append([i, tick[4], 1 if tick[1] > tick[2] else -1])
    return {"categoryData": category_data, "values": values, "volumes": volumes}

def calculate_ma(day_count: int, data):
    result: List[Union[float, str]] = []
    for i in range(len(data["values"])):
        if i < day_count:
            result.append("-")
            continue
        sum_total = 0.0
        for j in range(day_count):
            sum_total += float(data["values"][i - j][1])
        result.append(abs(float("%.3f" % (sum_total / day_count))))
    return result

def plot_stock_echarts(stock_code,last_day=90):
    """" 使用pyecharts绘制K线.
    """
    stock_data = get_stock_data(stock_code,last_day=90)
    chart_data = split_data(stock_data)

    kline_data = [data[1:-1] for data in chart_data["values"]]
    kline = (
        Kline()
        .add_xaxis(xaxis_data=chart_data["categoryData"])
        .add_yaxis(
            series_name="",
            y_axis=kline_data,
            itemstyle_opts=opts.ItemStyleOpts(color="#ec0000", color0="#00da3c"),
        )
        .set_global_opts(
            legend_opts=opts.LegendOpts(
                is_show=False, pos_bottom=10, pos_left="center"
            ),
            datazoom_opts=[
                opts.DataZoomOpts(
                    is_show=False,
                    type_="inside",
                    xaxis_index=[0, 1],
                    range_start=50,
                    range_end=100,
                ),
                opts.DataZoomOpts(
                    is_show=True,
                    xaxis_index=[0, 1],
                    type_="slider",
                    pos_top="85%",
                    range_start=50,
                    range_end=100,
                ),
            ],
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                splitarea_opts=opts.SplitAreaOpts(
                    is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                ),
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis",
                axis_pointer_type="cross",
                background_color="rgba(245, 245, 245, 0.8)",
                border_width=1,
                border_color="#ccc",
                textstyle_opts=opts.TextStyleOpts(color="#000"),
            ),
            visualmap_opts=opts.VisualMapOpts(
                is_show=False,
                dimension=2,
                series_index=5,
                is_piecewise=True,
                pieces=[
                    {"value": 1, "color": "#00da3c"},
                    {"value": -1, "color": "#ec0000"}, #ec0000
                ],
            ),
            axispointer_opts=opts.AxisPointerOpts(
                is_show=True,
                link=[{"xAxisIndex": "all"}],
                label=opts.LabelOpts(background_color="#777"),
            ),
            brush_opts=opts.BrushOpts(
                x_axis_index="all",
                brush_link="all",
                out_of_brush={"colorAlpha": 0.1},
                brush_type="lineX",
            ),
        )
    )

    line = (
        Line()
        .add_xaxis(xaxis_data=chart_data["categoryData"])
        .add_yaxis(
            series_name="MA5",
            y_axis=calculate_ma(day_count=5, data=chart_data),
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name="MA10",
            y_axis=calculate_ma(day_count=10, data=chart_data),
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name="MA20",
            y_axis=calculate_ma(day_count=20, data=chart_data),
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name="MA30",
            y_axis=calculate_ma(day_count=30, data=chart_data),
            is_smooth=True,
            is_hover_animation=False,
            linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
    )

    bar = (
        Bar()
        .add_xaxis(xaxis_data=chart_data["categoryData"])
        .add_yaxis(
            series_name="Volume",
            y_axis=chart_data["volumes"],
            xaxis_index=1,
            yaxis_index=1,
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                type_="category",
                is_scale=True,
                grid_index=1,
                boundary_gap=False,
                axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                axistick_opts=opts.AxisTickOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(is_show=False),
                axislabel_opts=opts.LabelOpts(is_show=False),
                split_number=20,
                min_="dataMin",
                max_="dataMax",
            ),
            yaxis_opts=opts.AxisOpts(
                grid_index=1,
                is_scale=True,
                split_number=2,
                axislabel_opts=opts.LabelOpts(is_show=False),
                axisline_opts=opts.AxisLineOpts(is_show=False),
                axistick_opts=opts.AxisTickOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(is_show=False),
            ),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )

    # Kline And Line
    overlap_kline_line = kline.overlap(line)

    # Grid Overlap + Bar
    grid_chart = Grid(
        init_opts=opts.InitOpts(
            width="500px",
            height="400px",
            animation_opts=opts.AnimationOpts(animation=False),
            theme = "dark",
            page_title = "Awesome-pyecharts",
        )
    )
    grid_chart.add(
        overlap_kline_line,
        grid_opts=opts.GridOpts(pos_left="10%", pos_right="8%", height="50%"),
    )
    grid_chart.add(
        bar,
        grid_opts=opts.GridOpts(
            pos_left="11%", pos_right="8%", pos_top="63%", height="16%"
        ),
    )

    return grid_chart
    # if html:
    #     grid_chart.render("professional_kline_brush.html")
    # else:
    #     grid_chart.render_notebook()


if __name__=="__main__":
    grid_chart = plot_stock_echarts('002247')
    grid_chart.render('test.html')








