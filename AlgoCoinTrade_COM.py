# -*- coding: utf-8 -*-
'''
# 알고리즘 코인 트래이딩 시스템
# Auth : mrtom17
# AlgoCoinTrade_COM.py
'''
# import Lib
import time, json , os , requests, yaml
import pyupbit
from datetime import datetime

svc_type = ''

if svc_type == 'local':
    conf_json = "/Users/tom.my/Public/Study/AlgoCoinTrade/config.json"
    conf_yaml = "/Users/tom.my/Public/Study/AlgoCoinTrade/coin.yaml"
    LOG_FILE_DIR = '/Users/tom.my/Public/Study/AlgoCoinTrade/log'
    LOG_FILE_NAME = '/Users/tom.my/Public/Study/AlgoCoinTrade/log/xrp_krw.log'
else:
    conf_json = "/home/ubuntu/AlgoCoinTrade/config.json"
    conf_yaml = "/home/ubuntu/AlgoCoinTrade/coin.yaml"
    LOG_FILE_DIR = '/home/ubuntu/AlgoCoinTrade/log'
    LOG_FILE_NAME = '/home/ubuntu/AlgoCoinTrade/log/xrp_krw.log'

with open(conf_json, 'r') as in_file:
    config = json.load(in_file)
    my_access = config['access']
    my_secret = config['secret']
    my_slack = config['myslack_token']

with open(conf_yaml, encoding='UTF-8') as f:
    _cfg = yaml.load(f, Loader=yaml.FullLoader)


def conn_upbit():

    access = my_access
    secret = my_secret
    upbit_conn = pyupbit.Upbit(access , secret)

    if upbit_conn:
        rst = upbit_conn
    else:
        rst = -1
    
    return rst

def set_logging(msg) -> None:

    if os.path.exists(LOG_FILE_NAME):
        with open(LOG_FILE_NAME, 'at', encoding='utf-8') as lfile:
            logmsg = datetime.now().strftime('[%y-%m-%d %H:%M:%S] ') + str(msg) + '\n'
            lfile.write(logmsg)
            lfile.close()
    else:
        os.mkdir(LOG_FILE_DIR)
        with open(LOG_FILE_NAME, 'at', encoding='utf-8') as lfile:
            logmsg = datetime.now().strftime('[%y-%m-%d %H:%M:%S] ') + str(msg) + '\n'
            lfile.write(logmsg)
            lfile.close()


def send_slack_msg(channel, text):
    myToken = my_slack
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+myToken},
        data={"channel": channel,"text": text}
    )
