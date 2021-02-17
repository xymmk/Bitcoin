import requests
import logging
import json
import hmac
import hashlib
import time
from datetime import datetime

global_base_price = 519
#差額
difference_price = 20000


def jpy_balance():
    timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
    method    = 'GET'
    endPoint  = 'https://api.coin.z.com/private'
    path      = '/v1/account/margin'
    try:
        text = timestamp + method + path
        sign = hmac.new(bytes(secretKey.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()
        headers = {
            "API-KEY": apiKey,
            "API-TIMESTAMP": timestamp,
            "API-SIGN": sign
        }
        res = requests.get(endPoint + path, headers=headers)
        response_data = json.loads(json.dumps(res.json()))
        if not 'status' in response_data.keys():
            return {"error": "cannot get kanban"}
        status = response_data["status"]
        if status != 0 :
            return {"error": status}
        availableAmount = response_data["data"]["availableAmount"]
        return {"availableAmount": int(availableAmount)}
         
    except:
        return {"error", "cannot get balance"}

def order(price, size, side):
    timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
    method    = 'POST'
    endPoint  = 'https://api.coin.z.com/private'
    path      = '/v1/order'
    reqBody = {
        "symbol": "BTC",
        "side": side,
        "executionType": "LIMIT",
        "timeInForce": "FAS",
        "price": str(price),
        "size": "0.0001"
    }

    text = timestamp + method + path + json.dumps(reqBody)
    sign = hmac.new(bytes(secretKey.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()
    headers = {
        "API-KEY": apiKey,
        "API-TIMESTAMP": timestamp,
        "API-SIGN": sign
    }

    res = requests.post(endPoint + path, headers=headers, data=json.dumps(reqBody))
    return res.json()

def get_price():
    endPoint = 'https://api.coin.z.com/public'
    path     = '/v1/ticker?symbol=BTC'
    response = requests.get(endPoint + path)
    # json.loads(json.dumps(res.json()))
    response_data = json.loads(json.dumps(response.json()))
    if not "status" in response_data:
        time.sleep(1)
        return get_price()
    status = response_data["status"]
    if int(status) != 0:
        time.sleep(1)
        return get_price()
    price = response_data["data"][0]["last"]
    return {"price": int(price)}

def assets():
    timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
    method    = 'GET'
    endPoint  = 'https://api.coin.z.com/private'
    path      = '/v1/account/assets'

    text = timestamp + method + path
    sign = hmac.new(bytes(secretKey.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()

    headers = {
        "API-KEY": apiKey,
        "API-TIMESTAMP": timestamp,
        "API-SIGN": sign
    }
    res = requests.get(endPoint + path, headers=headers)
    response_data = json.loads(json.dumps(res.json()))
    return float(response_data["data"][1]["amount"])



def sell(sell_price, base_price, sell_count, assets):
    if sell_price > global_base_price:
        if assets - sell_count * 0.0001 < 0.0498:
            print("比特币过低")
            return {"result": 0, "count": sell_count}
        order_sell_result = order(base_price + difference_price, '0.0001', "SELL")
        return {"result": order_sell_result, "count": sell_count + 1}
    return {"result": 0, "count": sell_count}

def buy(sell_price,balance, base_price):
    if balance < 500:
        print("余力は足りません")
        return 0
    # 比起余力低的话就买0.0001个
    if sell_price < global_base_price:
        order_sell_result = order(base_price - difference_price, '0.0001', "BUY")
        return order_sell_result
    return 0
    
if __name__ == "__main__":
    sell_count = 0
    while True:
        jpy_balance_dict = jpy_balance()
        base_price = get_price()["price"]
        sell_price = base_price * 0.0001

        if "error" in jpy_balance_dict:
            print("余力情報取れていませんでした")
            continue
        
        print("取引開始")
        print("sell_price: " + str(sell_price) + " base_price: " + str(base_price))
        print("buy " + str(buy(sell_price,jpy_balance_dict["availableAmount"], base_price)))
        sell_result = sell(sell_price, base_price, sell_count, assets())
        print("sell " + str(sell_result["result"]))
        sell_count = sell_result["count"]
        print("取引終了")
        time.sleep(3)