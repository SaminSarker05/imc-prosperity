from datamodel import OrderDepth, TradingState, Order
from typing import *
import string


class Trader:
    """
        weighted mid price with volume imbalance strategy
        - calculate fair price with volume weighted average of best bid ask prices
        - adjust fair price based on volume imbalance in order book
            - scale by half of bid-ask spread
    """

    def run(self, state: TradingState):
        print("traderData:", state.traderData)
        print("meta observations:", state.observations)
        result = {}

        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            fair_price = 10

            # require outstanding buy/sell orders in market
            if len(order_depth.sell_orders) != 0 and len(order_depth.buy_orders) != 0:
                ask_price, ask_vol = list(order_depth.sell_orders.items())[0]
                bid_price, bid_vol = list(order_depth.buy_orders.items())[0]

                if ask_vol + bid_vol > 0:
                    mid_price = ((ask_price * ask_vol) + (bid_price * bid_vol)) / (ask_vol + bid_vol)
                    volume_imbalance = (bid_vol - ask_vol) / (bid_vol + ask_vol)
                    spread = ask_price - bid_price
                    fair_price = mid_price + (volume_imbalance * spread / 2)

            if len(order_depth.sell_orders) != 0:
                ask_price, ask_quantity = list(order_depth.sell_orders.items())[0]
                if ask_price < fair_price:  # buy if below fair value
                    print("BUY", -ask_quantity, product, "@" + str(ask_price))
                    orders.append(Order(product, ask_price, -ask_quantity))
            
            if len(order_depth.buy_orders) != 0:
                bid_price, bid_quantity = list(order_depth.buy_orders.items())[0]
                if bid_price > fair_price:  # sell if above fair value
                    print("SELL", bid_quantity, product, "@" + str(bid_price))
                    orders.append(Order(product, bid_price, -bid_quantity))
            
            result[product] = orders

        traderData = "Trader class memory..."
        return result, 1, traderData
