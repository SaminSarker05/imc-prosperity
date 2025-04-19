"""
    - add logic for not exceding position limits
    current shells = 49

    [NOW]
    - add pnl metric to compute algo performance from logs
    - add sharpe ratio
"""


from datamodel import OrderDepth, TradingState, Order
from typing import *
import string

{
    "pnl": 0.0,
    "positions": {}
}


class Trader:
    # global vars for posiiton limits
    MAX_POS = 10

    """
        weighted mid price with volume imbalance strategy
        - calculate fair price with volume weighted average of best bid ask prices
        - adjust fair price based on volume imbalance in order book
            - scale by half of bid-ask spread
    """

    def run(self, state: TradingState):
        # store pnl cash and position of each product in traderData memory
        # differentiate between realized and unrealized pnl
        memory = state.traderData if state.traderData else {
            "pnl": 0.0,
            "positions": {}
        }

        # calculate realized pnl by processing own trades from last iteration 
        for product, trades in state.own_trades.items():  # dict of Trade objects
            for trade in trades:
                price = trade.price
                qty = trade.quantity  # pos if buy trade, neg if sell

                prev_pos = memory["positions"].get(product, 0)
                memory["positions"][product] = prev_pos + qty

                memory["pnl"] += (price * -qty)

        print("total pnl: ", memory["pnl"])

        result = {}

        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            fair_price: float = 10.0

            # current position for product
            position = memory["positions"].get(product, 0)

            # calculate fair price value using outstanding orders in market
            if len(order_depth.sell_orders) != 0 and len(order_depth.buy_orders) != 0:
                ask_price, ask_vol = list(order_depth.sell_orders.items())[0]
                bid_price, bid_vol = list(order_depth.buy_orders.items())[0]

                if ask_vol + bid_vol > 0:
                    mid_price = ((ask_price * ask_vol) + (bid_price * bid_vol)) / (ask_vol + bid_vol)

                    # [LOGIC] here
                    volume_imbalance = (bid_vol - ask_vol) / (bid_vol + ask_vol)
                    spread = ask_price - bid_price
                    fair_price = mid_price + (volume_imbalance * spread / 2)

            # build and place order, ensure positon limit respected

            if len(order_depth.sell_orders) != 0:
                ask_price, ask_qty = list(order_depth.sell_orders.items())[0]
                if ask_price < fair_price:  # BUY if product below fair price value
                    # quantities in sell order are negative so negate to get correct volume
                    
                    # ensure BUY position below product limit
                    buy_qty = min(-ask_qty, MAX_POS - position)
                    if buy_qty > 0:
                        orders.append(Order(product, ask_price, buy_qty))
                        print("BUY", buy_qty, product, "@" + str(ask_price))
            
            if len(order_depth.buy_orders) != 0:
                bid_price, bid_qty = list(order_depth.buy_orders.items())[0]
                if bid_price > fair_price:  # SELL product price if above fair value
                    # ensure SELL only if existing outstanding position
                
                    sell_qty = min(bid_qty, position)
                    if sell_qty > 0:
                        orders.append(Order(product, bid_price, -sell_qty))
                        print("SELL", sell_qty, product, "@" + str(bid_price))
            
            result[product] = orders

        traderData = memory
        return result, 1, traderData
