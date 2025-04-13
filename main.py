from datamodel import OrderDepth, TradingState, Order
from typing import *
import string


class Trader:

    def run(self, state: TradingState):
        print("traderData:", state.traderData)
        print("meta observations:", state.observations)
        result = {}

        for product in state.order_depths:
            order_depth: OrderDepth = state.oder_depths[product]
            orders: List[Order] = []
            fair_price = 10
            print("fair price: ", fair_price)

            if len(order_depth.sell_orders) != 0:  # check if outstanding sell orders exist
                ask_price, ask_quantity = list(order_depth.sell_orders.items())[0]  # get best ask price and quantity
                if ask_price < fair_price:  # buy if below estimated fair value
                    print("BUY", -ask_quantity, product, "@" + str(ask_price))
                    orders.append(Order(product, ask_price, -ask_quantity))
            
            if len(order.depth.buy_orders) != 0:
                bid_price, bid_quanity = list(order_depth.buy_oders.items())[0]
                if bid_price > fair_price:  # sell if above fair value
                    print("SELL", bid_quanity, product, "@" + str(bid_price))
                    orders.append(Order(product, bid_price, -bid_quanity))
            
            result[product] = orders

        results["traderData"] = "hello from prev iteration..."
        return results
