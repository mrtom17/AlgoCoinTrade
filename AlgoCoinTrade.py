# -*- coding: utf-8 -*-
'''
# 알고리즘 코인 트래이딩 시스템
# Auth : mrtom17
# AlgoCoinTrade.py
'''
# import Lib
import time, sys
import pyupbit
import datetime
import AlgoCoinTrade_COM as ausc

# 필요한 arg 정의 한다
setlog = ausc.set_logging


# Message 정의
msg_end = 'Upbit Auto Trading Process Closing. Process self- destructed'
msg_resell = '`sell_all() returned True -> 전날 잔여 코인 매도!`'
msg_proc = 'The AlogoCoinTrading process is still alive'
msg_sellall = '`sell_all() returned True -> 변동성 돌파 거래 코인 매도 성공 and self-destructed!`'
msg_sellfail = '`sell_all() returned False -> 변동성 돌파 거래 코인 매도 실패 and self-destructed!`'

def get_mycoin_balance(coin):

    #print(coin)
    upbitConn = ausc.conn_upbit()
    my_upbit_info = upbitConn.get_balances()
    #print(my_upbit_info)
    for coins in my_upbit_info:
        coin_name = coins['currency']
        coin_bal = float(coins['balance'])

        if coin_name == coin:
            return coin_name, coin_bal

    if coin == 'ALL':
        return my_upbit_info
    else:
        return None, 0

def get_start_time(ticker):
    # 시작 시간 조회
    df = pyupbit.get_ohlcv(ticker,interval='day',count=1)
    start_time = df.index[0]
    return start_time


def set_coin_target_price(coin, bestk):
    try:
        df = pyupbit.get_ohlcv(coin, interval='day', count=20)
        target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * bestk
        closes = df['close'].sort_index()
        _ma5 = closes.rolling(window=5).mean()
        _ma10 = closes.rolling(window=10).mean()
        ma5 = _ma5.iloc[-1]
        ma10 = _ma10.iloc[-1]
        return int(target_price) , int(ma5), int(ma10)

    except Exception as ex:
        setlog("`get_target_price() -> exception! " + str(ex) + "`")
        return None , None , None

def get_sellable_coin():
    try:
        sell_able_list = []
        upbitConn = ausc.conn_upbit()
        my_upbit_info = upbitConn.get_balances()
        for coins in my_upbit_info:
            if coins['currency'] =='KRW':
                continue
            ticker = 'KRW-'+coins['currency']
            coin_buy_price = float(coins['avg_buy_price'])

            current_price = pyupbit.get_orderbook(ticker=ticker)['orderbook_units'][0]['ask_price']
            target_profit = coin_buy_price * 0.03
            target_sell_price = coin_buy_price + target_profit

            if current_price >= target_sell_price :
                print(ticker,current_price,target_sell_price )
                sell_able_list.append([ticker,float(coins['balance'])])
            time.sleep(1)
        return sell_able_list
    except Exception as ex:
        setlog("`get_target_price() -> exception! " + str(ex) + "`")

def _buy_coin(coin, bestk):
    try:
        global buy_done_list
        if coin in buy_done_list:
            return False
        target_price, ma5, ma10 = set_coin_target_price(coin,bestk)
        current_price = pyupbit.get_orderbook(ticker=coin)['orderbook_units'][0]['ask_price']
        buy_qty = 0

        if current_price > 0 and buy_amount > 10000:
            buy_qty = int(buy_amount // current_price)
        else:
            return False

        if buy_qty < 1:
            return False

        if current_price > target_price and current_price > ma5 and current_price > ma10:
            setlog(str(coin) + '는 주문 수량 (' + str(buy_qty) +') EA : ' + str(current_price) + ' meets the buy condition!`')
            upbit_conn = ausc.conn_upbit()
            ret = upbit_conn.buy_market_order(coin,buy_amount)
            if ret:
                setlog('변동성 돌파 매수 주문 성공 -> 코인('+str(coin)+') 매수가격 ('+str(current_price)+')')
                buy_done_list.append(coin)
                return True
            else:
                setlog('변동성 돌파 매수 주문 실패 -> 코인('+str(coin)+')')
                return False
    except Exception as ex:
        setlog("`_buy_coin("+ str(coin) + ") -> exception! " + str(ex) + "`")

def _sell_each_coin(sell_able_list) -> None:
    try:

        upbit_conn = ausc.conn_upbit()
        coins = sell_able_list
        sell_done_coins = []
        for c in coins:
            ticker = c[0]
            balance = float(c[1])
            ret = upbit_conn.sell_market_order(ticker,balance)
            if ret :
                setlog('변동성 돌파 매도 주문(수익율 3% 도달) 성공 -> 코인('+str(ticker)+')')
            else:
                setlog('변동성 돌파 매도 주문(수익율 3% 도달) 실패 -> 코인('+str(ticker)+')')
    
    except Exception as ex:
        setlog("sell_each_all() -> exception! " + str(ex))

def _sell_coin():
    try:
        while True:
            upbit_conn = ausc.conn_upbit()
            coins = get_mycoin_balance('ALL')
            total_qty = 0
            for c in coins:
                if c['currency'] == 'KRW':
                    continue
                total_qty += float(c['balance'])
            if total_qty > 0 and total_qty < 1:
                return True

            for c in coins:
                if c['currency'] != 'KRW' and float(c['balance']) > 1:
                    ticker = 'KRW-'+c['currency']
                    balance = float(c['balance'])
                    ret = upbit_conn.sell_market_order(ticker,balance)
                    if ret :
                        setlog('변동성 돌파 매도 주문 성공 -> 코인('+str(ticker)+')')
                    else:
                        setlog('변동성 돌파 매도 주문 실패 -> 코인('+str(ticker)+')')
                time.sleep(1)
            time.sleep(5)
    except Exception as ex:
        setlog("sell_all() -> exception! " + str(ex))


if __name__ == '__main__':
    try:
        if ausc.conn_upbit() == -1:
            setlog('Upbit Connection Fail and retry')
            time.sleep(3)
            ausc.conn_upbit()

        coin_list = ausc._cfg['coinlist']
        buy_done_list = []
        target_buy_count = 3
        buy_percent = 0.33
        coin_name, total_cash = get_mycoin_balance('KRW')
        buy_amount = (total_cash * buy_percent) * 0.9995
        soldout = False
        setlog('----------------100% 증거금 주문 가능 금액 :'+str(total_cash))
        setlog('----------------종목별 주문 비율 :'+str(buy_percent))
        setlog('----------------종목별 주문 금액 :'+str(buy_amount))

        while True:
            t_now = datetime.datetime.now()
            t_00 = t_now.replace(hour=0, minute=0, second=0, microsecond=0)
            t_start = t_now.replace(hour=0, minute=5, second=0, microsecond=0)
            t_sell = t_now.replace(hour=23, minute=50, second=0, microsecond=0)
            t_exit = t_now.replace(hour=23, minute=55, second=0,microsecond=0)
            # 00:00:00 ~ 00:05:00 잔여 코인 전량 매도
            if t_00 < t_now < t_start and soldout == False:
                soldout = True
                if _sell_coin():
                    setlog(msg_resell)
                    ausc.send_slack_msg("#stock", msg_resell)
            # 00:05:00 ~ 23:50:00 변동성 돌파 매수 진행               
            if t_start < t_now < t_sell:
                for coin in coin_list:
                    if len(buy_done_list) < target_buy_count:
                        _buy_coin(coin[0], coin[1])
                        time.sleep(1)
                if t_now.minute == 30:
                    ausc.send_slack_msg("#stock", msg_proc)
                    time.sleep(5)
                sell_able_list = get_sellable_coin()
                if len(sell_able_list) > 0:
                    _sell_each_coin(sell_able_list)
            # 23:50:00 ~ 23:55:00 변동성 매수 물량 전량 매도, 프로세스 종료
            if t_sell < t_now < t_exit:
                if _sell_coin() == True:
                    setlog(msg_sellall)
                    ausc.send_slack_msg("#stock",msg_sellall)
                    sys.exit(0)
            time.sleep(3)

    except Exception as ex:
        setlog('`main -> exception! ' + str(ex) + '`')