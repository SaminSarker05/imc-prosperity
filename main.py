"""
    CURRENT_SHELLS = 49
    - MY STRATS
        volume weighted midprice with imbalance adjustment
        alpha indications through bid/ask spread and price margins
            more aggresive on wider spreads

    [TOdo]

    [DONE]
    - add pnl metric to compute algo performance from logs
    - add logic for not exceding position limits
    - add actual limits for each product
"""

from datamodel import OrderDepth, TradingState, Order
from typing import *
import string


class Trader:
    # class level dict for position limits
    MAX_POS = {
        "MAGNIFICENT_MACARONS": 75,
        "VOLCANIC_ROCK": 400,
        "CROISSANTS": 250,
        "JAMS": 350,
        "DJEMBES": 60,
        "PICNIC_BASKET1": 60,
        "PICNIC_BASKET2": 100
    }

    def calculate_fair_price(self, order_depth: OrderDepth) -> Tuple[float, float, float]:
        if not order_depth.sell_orders or not order_depth.buy_orders:
            return 10.0, 0, 0

        # calculate fair price value using outstanding orders in market
        ask_price, ask_vol = list(order_depth.sell_orders.items())[0]
        bid_price, bid_vol = list(order_depth.buy_orders.items())[0]

        # if ask_vol + bid_vol > 0:
        mid_price = ((ask_price * ask_vol) + (bid_price * bid_vol)) / (ask_vol + bid_vol)

        spread = ask_price - bid_price
        vol_imbalance = (bid_vol - ask_vol) / (bid_vol + ask_vol)
        fair_price = mid_price + (vol_imbalance * spread / 2)
        
        return fair_price, vol_imbalance, spread
        

    def run(self, state: TradingState):
        # store pnl cash and position of each product in traderData memory
        # differentiate between realized and unrealized pnl
        memory = state.traderData if state.traderData else {
            "cash": 0.0,
            "positions": {}
        }

        # process own trades from last run to calculate realized pnl and position
        for product, trades in state.own_trades.items():  # dict of Trade objects
            for trade in trades:
                price = trade.price
                qty = trade.quantity  # positive if buy, negative if sell

                prev_pos = memory["positions"].get(product, 0)
                memory["positions"][product] = prev_pos + qty

                # realized or executed cash
                memory["cash"] += (price * -qty)

        print("total pnl: ", memory["cash"])

        result = {}

        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            price_margin = 0
            max_pos_limit = self.MAX_POS.get(product, 0)

            # current position for product
            position = memory["positions"].get(product, 0)

            # calculate fair price of product
            fair_price, vol_imbalance, spread = calculate_fair_price(order_depth)
            
            # reduce market noise with price margin, using spread for aggresiveness
            if spread:
                if spread < 2:
                    price_margin = 0.1
                elif spread < 5:
                    price_margin = 0.5
                else:
                    price_margin = 1
            
            # build and place order, ensure positon limit respected

            if len(order_depth.sell_orders) != 0:
                ask_price, ask_qty = list(order_depth.sell_orders.items())[0]
                if ask_price < (fair_price - price_margin):  # BUY if product below fair price value
                    # quantities in sell order are negative so negate to get correct volume
                    
                    # ensure BUY position below product limit
                    buy_qty = min(-ask_qty, max_pos_limit - position)
                    if buy_qty > 0:
                        orders.append(Order(product, ask_price, buy_qty))
                        print("BUY", buy_qty, product, "@" + str(ask_price))
            
            if len(order_depth.buy_orders) != 0:
                bid_price, bid_qty = list(order_depth.buy_orders.items())[0]
                if bid_price > (fair_price + price_margin):  # SELL product price if above fair value
                    # ensure SELL only if existing outstanding position
                
                    sell_qty = min(bid_qty, position)
                    if sell_qty > 0:
                        orders.append(Order(product, bid_price, -sell_qty))
                        print("SELL", sell_qty, product, "@" + str(bid_price))
            
            result[product] = orders

        traderData = memory
        return result, 1, traderData
