#!/usr/bin/env python
# coding: utf-8

# https://github.com/algo2t/alphatrade

# In[1]:


import os
import enum
import configparser
from omspy_brokers.sasonline import Sasonline
from toolkit.fileutils import Fileutils
from toolkit.utilities import Utilities
from toolkit.logger import Logger
import pathlib

# In[4]:

fpath = "../../../"

cred = Fileutils().get_lst_fm_yml(fpath + "sas.yaml")
print(cred)


# In[8]:


sas = Sasonline(**cred)
if sas.authenticate():
    print("\n successfully authenticated")


# In[9]:


parser = configparser.ConfigParser()
parser.read('config.ini')
configuration_details = dict(parser.items("DEFAULT"))
sl_percentage = float(configuration_details["sl_percentage"])
profit_percentage = float(configuration_details["profit_percentage"])
threshold_percentage = float(configuration_details["threshold_percentage"])
is_move_stop_hard = bool(int(configuration_details["is_move_stop_hard"]))


class TransactionType(enum.Enum):
    Buy = 'BUY'
    Sell = 'SELL'


class OrderType(enum.Enum):
    Market = 'MARKET'
    Limit = 'LIMIT'
    StopLossLimit = 'SL'
    StopLossMarket = 'SL-M'


class ProductType(enum.Enum):
    Intraday = 'I'
    Delivery = 'D'
    CoverOrder = 'CO'
    BracketOrder = 'BO'


# In[ ]:


order_tracker = []


def track_orders():
    global order_tracker
    for order in sas_orders["data"]["completed_orders"]:
        if order["order_status"] == "complete":
            for tracked_order in order_tracker:
                if order["oms_order_id"] in tracked_order["algo_placed_order_id"]:
                    print("order complete for algo placed order. Squaring off")
                    tracked_order["square_off"] = 1
                    if sum(1
                           for d in order_tracker for k, v in d.items()
                           if (k == "trading_symbol" and v == order["instrument_token"] and "square_off" in d)
                           ) == 1:
                        sas.broker.unsubscribe(sas.broker.get_instrument_by_symbol(
                            order["exchange"], order["instrument_token"]), 1)
                    break
            else:
                def place_new_sl_order():
                    # Place 3% SL order on receipt of order from trader
                    args = {
                        "transaction_type": TransactionType.Sell,
                        # exchange will always be NfO?
                        "instrument": sas.broker.get_instrument_by_token(order["exchange"], order["instrument_token"]),
                        "quantity": order["quantity"],
                        "order_type": OrderType.StopLossMarket,
                        "product_type": order["product"],
                        "price": 0.0,
                        "trigger_price": order["price"] * (1 - sl_percentage / 100)
                    }
                    status = sas.order_place(**args)
                    return status['data']['oms_order_id']

                new_entry_to_tracker = {}
                new_entry_to_tracker["algo_placed_order_id"] = place_new_sl_order(
                )
                new_entry_to_tracker["trader_placed_order_id"] = order["oms_order_id"]
                new_entry_to_tracker["price"] = float(order["price"])
                new_entry_to_tracker["quantity"] = int(order["quantity"])
                new_entry_to_tracker["trading_symbol"] = order["trading_symbol"]
                new_entry_to_tracker["instrument_token"] = order["instrument_token"]
                new_entry_to_tracker["exchange"] = order["exchange"]
                new_entry_to_tracker["product"] = order["product"]

                # unsubscribe
                sas.broker.subscribe(sas.broker.get_instrument_by_symbol(
                    order["exchange"], order["instrument_token"]), 1)
                order_tracker.append(new_entry_to_tracker)

            print(order)


# In[ ]:


socket_opened = False
ltp_symbol_dict = {}


def event_handler_quote_update(message):
    global ltp_symbol_dict, order_tracker
    print(f"quote update {message}")

    symbol = message["trade_symbol"]
    ltp = message["ltp"]
    ltp_symbol_dict[symbol] = ltp
    for order in order_tracker:
        if order["trading_symbol"] == symbol:
            if ltp < order["price"] * (1 - sl_percentage / 100):
                # SL limit has reached
                # manually do something?
                pass
            elif order["price"] * (1 + threshold_percentage / 100) > ltp > order["price"] * (1 + profit_percentage / 100) and is_move_stop_hard:
                args = {
                    "transaction_type": TransactionType.Sell,
                    # exchange will always be NfO?
                    "instrument": sas.broker.get_instrument_by_token(order["exchange"], order["instrument_token"]),
                    "quantity": order["quantity"],
                    "order_type": OrderType.StopLossMarket,
                    "product_type": order["product"],
                    "price": 0.0,
                    "trigger_price": order["price"] * (1 + threshold_percentage / 100)
                }
                _ = sas.order_modify(**args)
            elif ltp >= order["price"] * (1 + profit_percentage / 100):
                args = {
                    "transaction_type": TransactionType.Sell,
                    # exchange will always be NfO?
                    "instrument": sas.broker.get_instrument_by_token(order["exchange"], order["instrument_token"]),
                    "quantity": order["quantity"],
                    "order_type": OrderType.StopLossMarket,
                    "product_type": order["product"],
                    "price": 0.0,
                    "trigger_price": order["price"] * (1 + profit_percentage / 100)
                }
                _ = sas.order_modify(**args)
                order["square_off"] = 1
                if sum(1
                        for d in order_tracker for k, v in d.items()
                        if (k == "trading_symbol" and v == order["instrument_token"] and "square_off" not in d)
                       ) == 1:
                    sas.broker.unsubscribe(sas.broker.get_instrument_by_symbol(
                        order["exchange"], order["instrument_token"]), 1)


def open_callback():
    global socket_opened
    socket_opened = True


def run_statergy():
    sas.broker.start_websocket(subscribe_callback=event_handler_quote_update,
                               socket_open_callback=open_callback,
                               run_in_background=True)
    while (socket_opened == False):
        pass
    while True:
        track_orders()
