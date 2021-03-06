import pandas as pd
import numpy as np
from datetime import datetime
from myfinance.stockdata import StockData
import myfinance.static as stt
import os


class StockList:
    def __init__(self, list_name):
        self.libpath = '.\\Lib\\'
        self.libfilename = list_name + '.lib'
        self.libcol = ['Tickers', 'Name', 'Type', 'Exchange', 'Start', 'Latest', 'nfo', 'active']
        if not (os.path.isdir(self.libpath)):
            os.makedirs(os.path.join(self.libpath))
        if os.path.isfile(self.libpath + self.libfilename):
            self.library = self.load_list()
        else:
            self.library = pd.DataFrame(columns=self.libcol)

    def add_tickers_yf(self, items):
        for ticker in items:
            print('Current Ticker : ' + ticker)
            if np.any(self.library['Tickers'].to_numpy() == ticker):
                print('X - ' + ticker + ' is already in your library.')
            else:
                try:
                    yftick = StockData(ticker, is_yf=True)
                    self.library.loc[len(self.library)] = [ticker, yftick.get_name(), yftick.get_type(),
                                                           yftick.get_exchange(), yftick.get_start_timestamp(),
                                                           yftick.get_latest_timestamp(), True, True]
                    yftick.save_info()
                    yftick.save_history()
                    print('O - Ticker "' + ticker + '" has been added.')
                except:
                    print('X - Could not download the information.')
                    continue

    def add_tickers_yf_from_csv(self, csvfilepath):
        codetable = pd.read_csv(csvfilepath)
        for idx in range(0, len(codetable)):
            ticker = str(codetable['Code'][idx])
            print('Current Ticker : ' + ticker)
            if np.any(self.library['Tickers'].to_numpy() == ticker):
                print('X - ' + ticker + ' is already in your library.')
            else:
                try:
                    yftick = StockData(ticker, is_yf=True)
                    source = codetable.loc[idx]
                    yftick.info = source
                    nfo = False
                except:
                    print('X - Ticker "' + ticker + '" couldn\'t be added.')
                    continue
                if nfo:
                    yftick.save_info()
                yftick.sort_drop_dup()
                yftick.save_history()
                self.library.loc[len(self.library)] = [ticker, yftick.get_name(), yftick.get_type(),
                                                       yftick.get_exchange(), yftick.get_start_timestamp(),
                                                       yftick.get_latest_timestamp(), True, True]
                print('O - Ticker "' + ticker + '" has been added.')
        self.save_list()

    def update_list_yf(self):
        today_stamp = pd.Timestamp(datetime.today())
        up2date_stamp = pd.Timestamp(today_stamp.timestamp() - 3600 * 24, unit='s')
        need2update = (self.library['Latest'] < up2date_stamp).to_numpy()
        if np.any(need2update):
            for idx in need2update.nonzero()[0]:
                ticker = self.library.loc[idx, 'Tickers']
                finaldate = self.library.loc[idx, 'Latest']
                startdate = pd.Timestamp(finaldate.timestamp() + 3600 * 24, unit='s')
                yftick = self.load_ticker(idx)
                yftick.update_history(start=startdate.strftime('%Y-%m-%d'), end=None)
                yftick.sort_drop_dup()
                yftick.save_history()
                self.library.loc[idx, 'Latest'] = yftick.get_latest_timestamp()
                print('Ticker "' + ticker + '" has been updated.')
        self.save_list()

    def kw_stock_codes_update(self, csvfilepath):
        today_stamp = pd.Timestamp(datetime.today())
        codetable = pd.read_csv(csvfilepath)
        code_list = []
        code_length = 6
        for idx in range(0, len(codetable)):
            if codetable['exchange'][idx] == 'KSC':
                ticker = str(codetable['Code'][idx]).zfill(code_length) + '.KS'
            elif codetable['exchange'][idx] == 'KOE':
                ticker = str(codetable['Code'][idx]).zfill(code_length) + '.KQ'
            else:
                ticker = str(codetable['Code'][idx])
            # print('Current Ticker : ' + ticker)
            if np.any(self.library['Tickers'].to_numpy() == ticker):
                tick_no = self.find_ticker_idx(ticker, exact=True)
                tickline = self.library.loc[tick_no]
                active = tickline['active']
                isupdate, ref_stamp = stt.timestamp_comp_stockmarket(tickline['Latest'], today_stamp)
                if isupdate & active:
                    code_list.append(ticker[0:code_length])
            else:
                source = codetable.loc[idx]
                kwtick = StockData(ticker, is_yf=False)
                kwtick.info = source
                nfo = False
                active = True
                tick_no = len(self.library)
                latest_stamp = pd.Timestamp(0, unit='s')
                self.library.loc[tick_no] = [ticker, source['shortName'], source['quoteType'], source['exchange'],
                                             latest_stamp, latest_stamp, nfo, active]
                self.save_list()
                code_list.append(ticker[0:code_length])
                print('O - Ticker "' + ticker + '" has been added.')
        return code_list

    def kw_index_codes_update(self, csvfilepath):
        today_stamp = pd.Timestamp(datetime.today())
        codetable = pd.read_csv(csvfilepath)
        code_list = []
        code_length = 3
        for idx in range(0, len(codetable)):
            ticker = str(codetable['Code'][idx]).zfill(code_length) + '.KOR'
            # print('Current Ticker : ' + ticker)
            if np.any(self.library['Tickers'].to_numpy() == ticker):
                tick_no = self.find_ticker_idx(ticker, exact=True)
                tickline = self.library.loc[tick_no]
                active = tickline['active']
                isupdate, ref_stamp = stt.timestamp_comp_stockmarket(tickline['Latest'], today_stamp)
                if isupdate & active:
                    code_list.append(ticker[0:code_length])
            else:
                source = codetable.loc[idx]
                kwtick = StockData(ticker, is_yf=False)
                kwtick.info = source
                nfo = False
                active = True
                tick_no = len(self.library)
                latest_stamp = pd.Timestamp(0, unit='s')
                self.library.loc[tick_no] = [ticker, source['shortName'], source['quoteType'], source['exchange'],
                                             latest_stamp, latest_stamp, nfo, active]
                self.save_list()
                code_list.append(ticker[0:code_length])
                print('O - Ticker "' + ticker + '" has been added.')
        return code_list

    def find_ticker_idx(self, ticker, **kwargs):
        exact = kwargs['exact']
        if exact:
            restick = self.library[(self.library['Tickers'] == ticker)]
        else:
            restick = self.library[self.library['Tickers'].str.contains(ticker)]
        if len(restick.index) < 1:
            return -1
        else:
            return restick.index[0]

    def save_list(self):
        self.library.to_pickle(self.libpath + self.libfilename)

    def load_list(self):
        tickers = pd.read_pickle(self.libpath + self.libfilename)
        return tickers

    def is_ticker_file(self, idx):
        data = StockData(self.library['Tickers'][idx])
        return data.is_hist_file()

    def load_ticker(self, idx, is_yf=False):
        data = StockData(self.library['Tickers'][idx], is_yf=is_yf)
        if data.is_hist_file():
            data.load_history()
        return data

    def get_ticker(self, idx):
        return self.library['Tickers'][idx]
