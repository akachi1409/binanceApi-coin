# IMPORTS
import pandas as pd
import math
import os.path
import time
from binance.client import Client
from datetime import timedelta, datetime
from dateutil import parser
import schedule
import time
import sqlite3
from sqlite3 import Error

### API
binance_api_key = 'RANDOMKEY'    #Enter your own API-key here
binance_api_secret = 'RANDOMKEY' #Enter your own API-secret here

### CONSTANTS
binsizes = {"1m": 1, "5m": 5, "15m": 15, "1h": 60, "1d": 1440}
batch_size = 750
binance_client = Client(api_key=binance_api_key, api_secret=binance_api_secret)

binance_symbols = ["BTCUSDT", "SHIBUSDT", "ETHUSDT", "BUSDUSDT", "SANDUSDT", "SOLUSDT", "IOTXUSDT", "DOTUSDT",
"XRPUSDT", "BNBUSDT", "MANAUSDT", "ARPAUSDT", "ADAUSDT", "TRXUSDT", "AVAXUSDT", "AXSUSDT", "DOGEUSDT", "OMGUSDT", "LRCUSDT", "HOTUSDT",
"LUNAUSDT", "SLPUSDT", "FIDAUSDT", "MATICUSDT", "FTMUSDT", "FILUSDT", "ARUSDT", "BADGERUSDT", "USDCUSDT", "ATOMUSDT", "VETUSDT",
"BETAUSDT", "LINKUSDT", "CHZUSDT", "LTCUSDT", "CHRUSDT", "EOSUSDT", "SRMUSDT", "MKRUSDT", "EGLDUSDT", "C98USDT", "THETAUSDT", "IOSTUSDT", "BTTUSDT", "ICPUSDT",
"TLMUSDT", "ALGOUSDT", "ENJUSDT"]
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn
def delete_log(conn, log):
    sql = 'DELETE FROM dashboard_log WHERE symbol=? AND interval=?'
    cur = conn.cursor()
    cur.execute(sql, log)
    conn.commit()
def create_log(conn, log):
    sql = ''' INSERT INTO dashboard_log (symbol, timestamp, volume, interval) VALUES (?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, log)
    conn.commit()
    
def minutes_of_new_data(symbol, kline_size, data):
    if len(data) > 0:  old = parser.parse(data["timestamp"].iloc[-1])
    old = pd.to_datetime(binance_client.get_klines(symbol=symbol, interval=kline_size)[-2][0], unit='ms')
    new = pd.to_datetime(binance_client.get_klines(symbol=symbol, interval=kline_size)[-1][0], unit='ms')
    return old, new

def get_all_binance(conn, symbol, kline_size, save = False):
    data_df = pd.DataFrame()
    oldest_point, newest_point = minutes_of_new_data(symbol, kline_size, data_df)
    delta_min = (newest_point - oldest_point).total_seconds()/60
    available_data = math.ceil(delta_min/binsizes[kline_size])
    print('Downloading %d minutes of new data available for %s, i.e. %d instances of %s data.' % (delta_min, symbol, available_data, kline_size))
    klines = binance_client.get_historical_klines(symbol, kline_size, oldest_point.strftime("%d %b %Y %H:%M:%S"), newest_point.strftime("%d %b %Y %H:%M:%S"))
    data = pd.DataFrame(klines, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore' ])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    if len(data_df) > 0:
        temp_df = pd.DataFrame(data)
        data_df = data_df.append(temp_df)
    else: data_df = data
    data_df.set_index('timestamp', inplace=True)
    delete_log(conn, (symbol, kline_size))
    if save: 
        dict = data_df.to_dict()
        date_to_volume = dict.get('volume')
        for date in date_to_volume.keys():
            create_log(conn, (symbol, datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S'), date_to_volume[date], kline_size))
    print('All caught up..!')
    return data_df
def get_binance_per_1m(conn):
    for symbol in binance_symbols:
        get_all_binance(conn, symbol, '1m', save = True)
def get_binance_per_5m(conn):
    for symbol in binance_symbols:
        get_all_binance(conn, symbol, '5m', save = True)
def get_binance_per_15m(conn):
    for symbol in binance_symbols:
        get_all_binance(conn, symbol, '15m', save = True)
def get_binance_per_1h(conn):
    for symbol in binance_symbols:
        get_all_binance(conn, symbol, '1h', save = True)
def get_binance_per_1d(conn):
    for symbol in binance_symbols:
        get_all_binance(conn, symbol, '1d', save = True)

def main():
    database = r"db.sqlite3"
    conn = create_connection(database)
    args = conn
    with conn:
        schedule.every(1).minutes.do(get_binance_per_1m, args)
        schedule.every(5).minutes.do(get_binance_per_5m, args)
        schedule.every(15).minutes.do(get_binance_per_15m, args)
        schedule.every().hour.do(get_binance_per_1h, args)
        schedule.every().day.at("00:00").do(get_binance_per_1d, args)

        get_binance_per_1m(conn)
        get_binance_per_5m(conn)
        get_binance_per_15m(conn)
        get_binance_per_1h(conn)
        get_binance_per_1d(conn)

        while 1:
            schedule.run_pending()
            time.sleep(1)
main()