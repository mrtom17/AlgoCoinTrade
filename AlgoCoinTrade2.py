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
import AlgoCoinTrade_COM as accm

setlog = accm.set_logging

def get_mycoin_balance(coin):

    upbitConn = accm.conn_upbit()
    my_upbit_info = upbitConn.get_balances()

    for coins in my_upbit_info:
        coin_name = coins['currency']
        coin_bal = float(coins['balance'])

        if coin_name == coin:
            return coin_name, coin_bal

    if coin == 'ALL':
        return my_upbit_info
    else:
        return None, 0

def get_buy_coin_info(coin_list):
    try:

        coin_output = []
        for coin in coin_list:
            ticker = coin[0]
            bestk = coin[1]
            df = pyupbit.get_ohlcv(ticker, interval='day', count=10)
            target_price = df.iloc[8]['close'] + (df.iloc[8]['high'] - df.iloc[8]['low']) * bestk
            closes = df['close'].sort_index()
            _ma5 = closes.rolling(window=5).mean()
            _ma10 = closes.rolling(window=10).mean()
            ma5 = _ma5.iloc[-1]
            ma10 = _ma10.iloc[-1]
            _coin_output = {'coin' : ticker ,'target_p' : target_price , 'ma5' : ma5, 'ma10' : ma10}
            coin_output.append(_coin_output)
            time.sleep(0.5)
        return coin_output

    except Exception as ex:
        setlog("`get_target_price() -> exception! " + str(ex) + "`")
        return None    

def _buy_able_coin(infos):
    try:
        global coin_buy_done_list

        ticker = infos['coin']
        t_price = infos['target_p']
        _ma5 = infos['ma5']
        _ma10 = infos['ma10']

        current_price = pyupbit.get_orderbook(ticker=ticker)['orderbook_units'][0]['ask_price']

        if current_price > t_price and current_price > _ma5 and current_price > _ma10:
            if ticker not in coin_buy_done_list:
                _coin_output = {'coin' : ticker ,'target_p' : t_price , 'ma5' : _ma5, 'ma10' : _ma10}
                #print(_coin_output)
                coin_buy_able_list.append(_coin_output)
        
        return coin_buy_able_list

    except Exception as ex:
        setlog("`_buy_able_coin("+ str(ticker) + ") -> exception! " + str(ex) + "`")

def get_sellable_coin():
    try:
        global coin_buy_done_list

        if len(coin_buy_done_list) == 0:
            return False

        sell_able_list = []
        upbitConn = accm.conn_upbit()
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
                #print(ticker,current_price,target_sell_price )
                sell_able_list.append([ticker,float(coins['balance'])])
            time.sleep(1)
        return sell_able_list
    except Exception as ex:
        setlog("`get_target_price() -> exception! " + str(ex) + "`")

def _buy_coin(infos):
    try:
        global coin_buy_done_list

        ticker = infos['coin']
        t_price = infos['target_p']
        _ma5 = infos['ma5']
        _ma10 = infos['ma10']

        if ticker in coin_buy_done_list:
            return False

        _ , my_coin_qty = get_mycoin_balance(ticker[4:])

        print(ticker, my_coin_qty)

        if my_coin_qty > 1 :
            return False

        current_price = pyupbit.get_orderbook(ticker=ticker)['orderbook_units'][0]['ask_price']
        buy_qty = 0

        if current_price > 0 and buy_amount > 10000:
            buy_qty = int(buy_amount // current_price)
        else:
            return False

        if buy_qty < 1:
            return False

        if current_price > t_price and current_price > _ma5 and current_price > _ma10:
            setlog(str(ticker) + '는 주문 수량 (' + str(buy_qty) +') EA : ' + str(current_price) + ' meets the buy condition!`')
            upbit_conn = accm.conn_upbit()
            ret = upbit_conn.buy_market_order(ticker,buy_amount)
            if ret:
                setlog('변동성 돌파 매수 주문 성공 -> 코인('+str(ticker)+') 매수가격 ('+str(current_price)+')')
                coin_buy_done_list.append(ticker)
                return True
            else:
                setlog('변동성 돌파 매수 주문 실패 -> 코인('+str(ticker)+')')
                return False
    except Exception as ex:
        setlog("`_buy_coin("+ str(ticker) + ") -> exception! " + str(ex) + "`")

def _sell_each_coin(sell_able_list) -> None:
    try:

        upbit_conn = accm.conn_upbit()
        coins = sell_able_list

        for c in coins:
            ticker = c[0]
            balance = float(c[1])
            ret = upbit_conn.sell_market_order(ticker,balance)
            if ret :
                setlog('변동성 돌파 매도 주문(수익율 30% 도달) 성공 -> 코인('+str(ticker)+')')
            else:
                setlog('변동성 돌파 매도 주문(수익율 30% 도달) 실패 -> 코인('+str(ticker)+')')
            time.sleep(1)
        time.sleep(5)
    except Exception as ex:
        setlog("sell_each_all() -> exception! " + str(ex))


def _sell_coin():
    try:
        while True:
            upbit_conn = accm.conn_upbit()
            coins = get_mycoin_balance('ALL')
            total_qty = 0

            for c in coins:
                if c['currency'] == 'KRW':
                    continue
                total_qty += float(c['balance'])
            #print(total_qty)
            if total_qty >= 0 and total_qty < 1:
                return True

            for c in coins:
                if c['currency'] != 'KRW' and float(c['balance']) > 1:
                    ticker = 'KRW-'+c['currency']
                    balance = float(c['balance'])
                    ret = upbit_conn.sell_market_order(ticker,balance)
                    if ret:
                        setlog('변동성 돌파 매도 주문 성공 -> 코인('+str(ticker)+')')
                    else:
                        setlog('변동성 돌파 매도 주문 실패 -> 코인('+str(ticker)+')')
                time.sleep(1)
            time.sleep(5)
    except Exception as ex:
        setlog("sell_all() -> exception! " + str(ex))


if __name__ == '__main__':
    try:

        coin_list = accm._cfg['coinlist']
        target_coin_values = get_buy_coin_info(coin_list)
        coin_buy_done_list = []
        coin_buy_able_list = []
        coin_target_buy_count = 3
        buy_percent = 0.33
        coin_name, coin_cash = get_mycoin_balance('KRW')
        buy_amount = (coin_cash * buy_percent) * 0.9995
        soldout = False
        setlog('----------------100% 증거금 주문 가능 금액 :'+str(coin_cash))
        setlog('----------------종목별 주문 비율 :'+str(buy_percent))
        setlog('----------------종목별 주문 금액 :'+str(buy_amount))

        while True:

            # Message 정의
            msg_end = 'Upbit Auto Trading Process Closing. Process self- destructed'
            msg_resell = '`sell_all() returned True -> 전날 잔여 코인 매도!`'
            msg_proc = 'The AlogoCoinTrading process is still alive'
            msg_sellall = '`sell_all() returned True -> 변동성 돌파 거래 코인 매도 성공 and self-destructed!`'
            msg_sellfail = '`sell_all() returned False -> 변동성 돌파 거래 코인 매도 실패 and self-destructed!`'
            
            # 시간 정의
            t_now = datetime.datetime.now()
            t_sell_start = t_now.replace(hour=9, minute=5, second=0, microsecond=0)
            t_sell_end = t_now.replace(hour=9, minute=10, second=0, microsecond=0)
            t_buy_one = t_now.replace(hour=9, minute=30, second=0, microsecond=0)
            t_end_one = t_now.replace(hour=23, minute=59, second=59, microsecond=0)
            t_buy_two = t_now.replace(hour=0, minute=0, second=0, microsecond=0)
            t_end_two = t_now.replace(hour=8, minute=30, second=0, microsecond=0)
            t_exit = t_now.replace(hour=8, minute=40, second=0,microsecond=0)

            # 09:05:00 ~ 09:10:00 잔여 코인 전량 매도
            if t_sell_start < t_now < t_sell_end and soldout == False:
                soldout = True
                if _sell_coin() == True:
                    setlog('09:05:00 ~ 09:10:00 잔여 코인 전량 매도')
                    accm.send_slack_msg("#stock", '09:05:00 ~ 09:10:00 잔여 코인 전량 매도')

                    buy_percent = 0.33
                    coin_name, total_cash = get_mycoin_balance('KRW')
                    buy_amount = (total_cash * buy_percent) * 0.9995
                    setlog('----------------100% 증거금 주문 가능 금액 :'+str(total_cash))
                    setlog('----------------종목별 주문 비율 :'+str(buy_percent))
                    setlog('----------------종목별 주문 금액 :'+str(buy_amount))

            # 09:30:00 ~ 23:59:59 변동성 돌파 매수 진행           
            if t_buy_one < t_now < t_end_one:
                if len(coin_buy_done_list) < coin_target_buy_count:
                    for infos in target_coin_values:
                        lcoins = _buy_able_coin(infos)
                        time.sleep(1)
                    if len(lcoins) > 0 and len(lcoins) < 4:
                        for bcoin in lcoins:
                            _buy_coin(bcoin)
                            time.sleep(1)
                    if len(lcoins) > 4:
                        coin_target_buy_count = len(lcoins)
                        buy_percent = 1 / len(lcoins)
                        coin_name, coin_cash = get_mycoin_balance('KRW')
                        buy_amount = (coin_cash * buy_percent) * 0.9995
                        for bcoin in lcoins:
                            _buy_coin(bcoin)
                            time.sleep(1)
                if len(coin_buy_done_list) > 0:
                    sell_able_list = get_sellable_coin()
                    if len(sell_able_list) > 0:
                        _sell_each_coin(sell_able_list)
                if t_now.minute == 30 and 0 <= t_now.second <=10:
                    accm.send_slack_msg("#stock", msg_proc)
                time.sleep(5)
            # 00:00:00 ~ 08:30:00 변동성 돌파 매수 진행 
            if t_buy_two < t_now < t_end_two:
                if len(coin_buy_done_list) < coin_target_buy_count:
                    for infos in target_coin_values:
                        lcoins = _buy_able_coin(infos)
                        time.sleep(1)
                    if len(lcoins) > 0 and len(lcoins) < 4:
                        for bcoin in lcoins:
                            _buy_coin(bcoin)
                            time.sleep(1)
                    if len(lcoins) > 4:
                        coin_target_buy_count = len(lcoins)
                        buy_percent = 1 / len(lcoins)
                        coin_name, coin_cash = get_mycoin_balance('KRW')
                        buy_amount = (coin_cash * buy_percent) * 0.9995
                        for bcoin in lcoins:
                            _buy_coin(bcoin)
                            time.sleep(1)
                if len(coin_buy_done_list) > 0:
                    sell_able_list = get_sellable_coin()
                    if len(sell_able_list) > 0:
                        _sell_each_coin(sell_able_list)
                if t_now.minute == 30 and 0 <= t_now.second <=10:
                    accm.send_slack_msg("#stock", msg_proc)
                time.sleep(5)
            # 08:30:00 ~ 08:40:00 프로세스 종료
            if t_end_two < t_now < t_exit:
                accm.send_slack_msg("#stock",msg_end)
                sys.exit(0)
            time.sleep(3)
    except Exception as ex:
        setlog('`main -> exception! ' + str(ex) + '`')
