import pandas as pd
import numpy as np
from myfinance.constants import *


def timestamp_day_before_n_days(today_pandas, n=1):
    yesterday = pd.Timestamp(today_pandas.timestamp() - (n * 3600 * 24), unit='s')
    return yesterday


def timestamp_date_only(timestamp_pandas):
    return pd.Timestamp(timestamp_kw_str(timestamp_pandas))


def timestamp_comp_stockmarket(latest, today):
    time_ref = timestamp_ref_date(today)
    return latest < time_ref, time_ref


def timestamp_ref_date(today=pd.Timestamp.now()):
    if today.hour < 19:
        time_ref = timestamp_day_before_n_days(today)
    else:
        time_ref = today
    ref_weekday = time_ref.weekday()
    if ref_weekday > 4:
        time_ref = timestamp_day_before_n_days(time_ref, n=(ref_weekday - 4))
    time_ref = timestamp_date_only(time_ref)
    return time_ref


def timestamp_islatestworkingday(latest_date):
    timenow = pd.Timestamp.now()
    if timenow.hour > 19:
        today = timestamp_ref_date()
        delta = today - latest_date
        if today.weekday() == 0:
            ref_day = 3
        else:
            ref_day = 1
        if delta.days == ref_day:
            return True
        else:
            return False
    else:
        return False


def timestamp_kw_str(timestamp_pandas):
    return timestamp_pandas.strftime(STR_date)


def stock_table_indexing():
    """parameters shown in Tester UI"""
    return ['종목코드', '종목명', '현재가', '기준가', '전일대비', '등락율', '거래량', '매도호가', '매수호가']


def get_tick_size(current_price):
    if current_price < 1000:
        tick_size = 1
    elif current_price < 5000:
        tick_size = 5
    elif current_price < 10000:
        tick_size = 10
    elif current_price < 50000:
        tick_size = 50
    elif current_price < 100000:
        tick_size = 100
    elif current_price < 500000:
        tick_size = 500
    else:
        tick_size = 1000
    return tick_size