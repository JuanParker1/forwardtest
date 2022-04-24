from curses import start_color
from backtest.core import engine, helpers,data

# Global Imports
import pandas as pd

# Build mean reversion strategy
import talib
import os
import sys
# sys.path.append("../")

def load_data(start_date="2022-01-01", end_date="2022-03-30"):
    """
    The head of data:
    index   date  low  high  open  close  volume
    """
    data_file = f"{start_date}+{end_date}.csv"
    if os.path.exists(data_file):
        df = pd.read_csv(data_file)
    else:
        df = data.get_ltf_candles("USDC_BTC", "1-HOUR", f"{start_date} 00:00:00", f"{end_date} 00:00:00")
        df.to_csv(data_file)
    print(df.head())
    return df

def sma339(df, timeperiod=339):
    '''
    计算339均线
    '''
    close_price_series = df["close"].values
    l = talib.SMA(close_price_series, timeperiod=timeperiod)
    df['339']  = l
    return df

def touches(df):
    df['339_close_upper'] = df.close >= df['339']
    df['339_close_lower'] = df.close < df['339']
    return df

def 站稳339(a_candle):
    # 估计需要给个明确的站稳的含义
    return a_candle['339_close_upper']

def 跌破339(a_candle):
    return a_candle['339_close_lower']

def 回阴不破(a_candle):
    return True

def logic(account, lookback):
    try:
        lookback = helpers.period(lookback)
        this_hour = lookback.loc(0)
        last_hour = lookback.loc(-1)
        # 开仓
        if 站稳339(last_hour) and 回阴不破(this_hour):
            entry_price   = this_hour.close
            entry_capital = account.buying_power #全部买入，现在没有资金分配策略
            if entry_capital > 0: #判断是否开仓，可以用一个更好的状态机记录，TBD
                account.enter_position('long', entry_capital, entry_price)
        if 跌破339(last_hour) and 跌破339(this_hour):
            if account.buying_power <= 0:
                exit_price = this_hour.close
                for position in account.positions:
                    if position.type_ == 'long':
                        account.close_position(position, 1, exit_price)
        

    except Exception as e:
        print(e)
        pass # Handles lookback errors in beginning of dataset

# Apply strategy to example
#df = pd.read_csv("data/BTC_USD.csv", header=0, index_col=0)
df = load_data()
df = sma339(df)
df = touches(df)

# Backtest
backtest = engine.backtest(df)
backtest.start(1000, logic)
backtest.results()
