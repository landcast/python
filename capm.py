import pandas as pd
import tushare as ts

import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

import statsmodels.api as sm


def figure_roe(df, plt, font):
    for col in df.columns:
        plt.plot(df[col], label=col)
    plt.title('日收益率时序图(2017至今)', fontproperties=font)
    plt.legend()


def figure_accumulated_roe(df, plt, font=None):
    for col in df.columns:
        plt.plot((df[col]+1).cumprod()-1, label=col)
    if font:
        plt.title('累计收益率时序图(2017至今)', fontproperties=font)
    else:
        plt.title('累计收益率时序图(2017至今)')
    plt.legend()


def get_data_tushare():
    # 获取数据
    ts.set_token('055aeef55e85b461e45cdd27490eb684a523b8f8a6fc4669e11ea607')
    pro = ts.pro_api()
    wanke = pro.daily(ts_code='000002.SZ', start_date='20170101')
    pingan = pro.daily(ts_code='601318.SH', start_date='20170101')
    maotai = pro.daily(ts_code='600519.SH', start_date='20170101')
    wanhua = pro.daily(ts_code='002415.SZ', start_date='20170101')
    keda = pro.daily(ts_code='002230.SZ', start_date='20170101')
    hs300 = pro.index_daily(ts_code='000300.SH', start_date='20170101')

    # 仅保留收益率数据，且用日期作为index
    # 然后按照日期排序（增序）
    stock_list = [wanke, pingan, maotai, wanhua, keda, hs300]
    for stock in stock_list:
        stock.index = pd.to_datetime(stock.trade_date)

    df = pd.concat([stock.pct_chg / 100 for stock in stock_list], axis=1)
    df.columns = ['wanke', 'pingan', 'maotai', 'wanhua', 'keda', 'hs300']
    df = df.sort_index(ascending=True)
    # print(df)
    # print(df.describe())
    df = df.fillna(0)
    returns = (df + 1).product() - 1
    print('累计收益率：')
    print(returns)
    print('标准差：')
    print(df.std())
    print('')
    return df


def print_statsmodel(df_rp):
    stock_names = {
        'wanke': '万科A',
        'pingan': '中国平安',
        'maotai': '贵州茅台',
        'wanhua': '万华化学',
        'keda': '科大讯飞'
    }
    for stock in ['wanke', 'pingan', 'maotai', 'wanhua', 'keda']:
        model = sm.OLS(df_rp[stock], sm.add_constant(df_rp['hs300']))
        result = model.fit()
        print(stock_names[stock] + '')
        print(result.summary())
        print('')


if __name__ == '__main__':
    df = get_data_tushare()
    sns.set()
    font = FontProperties(fname='/usr/share/fonts/msyh.ttc', size=16)
    plt.figure(figsize=(10, 5))
    figure_accumulated_roe(df, plt, font)
    # plt.show()

    # 无风险收益率假定为0.032，rf为每日无风险收益
    rf = 1.032 ** (1 / 360) - 1
    print('risk free interest', rf)

    df_rp = df - rf
    print_statsmodel(df_rp)
    # print(df_rp.head())
    # sns.pairplot(df_rp)
    plt.show()



