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

if __name__ == '__main__':
    try:

        coin_list = accm._cfg['coinlist']
        coin_buy_done_list = []
        coin_target_buy_count = 3
        buy_percent = 0.33
        coin_name, coin_cash = get_mycoin_balance('KRW')
        buy_amount = (coin_cash * buy_percent) * 0.9995
        soldout = False
        setlog('----------------100% 증거금 주문 가능 금액 :'+str(coin_cash))
        setlog('----------------종목별 주문 비율 :'+str(buy_percent))
        setlog('----------------종목별 주문 금액 :'+str(buy_amount))

        while True:

            t_now = datetime.datetime.now()
            t_sell_start = t_now.replace(hour=9, minute=5, second=0, microsecond=0)
            t_sell_end = t_now.replace(hour=9, minute=10, second=0, microsecond=0)
            t_buy_one = t_now.replace(hour=9, minute=30, second=0, microsecond=0)
            t_end_one = t_now.replace(hour=23, minute=59, second=59, microsecond=0)
            t_buy_two = t_now.replace(hour=0, minute=0, second=0, microsecond=0)
            t_end_two = t_now.replace(hour=8, minute=30, second=0, microsecond=0)
            t_exit = t_now.replace(hour=8, minute=40, second=0,microsecond=0)

            # 09:05:00 ~ 09:10:00 잔여 코인 전량 매도
            if t_sell_start < t_now < t_sell_end:
                setlog('09:05:00 ~ 09:10:00 잔여 코인 전량 매도')
            # 09:30:00 ~ 23:59:59 변동성 돌파 매수 진행               
            if t_buy_one < t_now < t_end_one:
                setlog('09:30:00 ~ 23:59:59 변동성 돌파 매수 진행 ->' + str(coin_list))
                setlog('09:30:00 ~ 23:59:59 변동성 돌파 매수 진행 ->' + str(coin_buy_done_list))
                setlog('09:30:00 ~ 23:59:59 변동성 돌파 매수 진행 ->' + str(coin_target_buy_count))
                setlog('09:30:00 ~ 23:59:59 변동성 돌파 매수 진행 ->' + str(buy_percent))
                setlog('09:30:00 ~ 23:59:59 변동성 돌파 매수 진행 ->' + str(coin_cash))
                setlog('09:30:00 ~ 23:59:59 변동성 돌파 매수 진행 ->' + str(buy_amount))

                if t_now.minute == 30:
                    sys.exit(0)
                time.sleep(60)
            # 00:00:00 ~ 08:30:00 변동성 돌파 매수 진행 
            if t_buy_two < t_now < t_end_two:
                setlog('00:00:00 ~ 08:30:00 변동성 돌파 매수 진행')
                if t_now.minute == 30:
                    sys.exit(0)
                time.sleep(60)
            # 08:30:00 ~ 08:40:00 프로세스 종료
            if t_end_two < t_now < t_exit:
                setlog('08:30:00 ~ 08:40:00 프로세스 종료')

    except Exception as ex:
        setlog('`main -> exception! ' + str(ex) + '`')