from dataclasses import dataclass
from sortedcontainers import SortedDict, SortedSet
import datetime as dt
from collections import defaultdict, namedtuple

@dataclass
class Order:
    price : int
    qty : int
    time : int

class PriceQtyDict(SortedDict):
    """Like defaultdict, but sorted, for int only,
    and 0s remove themselves."""
    def __getitem__(self, key):
        return super().get(key, 0)
    
    def __setitem__(self, key, value):
        if value:
            super().__setitem__(key, value)
        elif key in self:
            del self[key]

class OrderQueue:
    def __init__(self, ascending = True):
        self.q = SortedDict()
        self.sign = 1 if ascending else -1
        self.price_qty = PriceQtyDict()
        self.orders_by_name = defaultdict(lambda: {})

    def add_order(self, order):
        key = (self.sign * order.price, order.time)
        self.q[key] = order
        self.price_qty[order.price] += order.qty
        self.orders_by_name[order.name][key] = order

    def cancel_order(self, price, time):
        key = (self.sign * order.price, order.time)
        order = self.q.pop(key)
        self.price_qty[price] -= order.qty
        self.orders_by_name[order.name].pop(key)

    def best_order(self):
        key, order = self.q.popitem()
        self.price_qty[order.price] -= order.qty
        self.orders_by_name[order.name].pop(key)
        return order

    def can_trade(self, price):
        return self.peekitem(0).price >= price

    def __repr__(self):
        return f"OrderQueue(len={len(self.q)}" if len(self.q) > 20 else repr(self.q)

class OrderQueue(SortedSet):

    Dummy = namedtuple('Dummy', ['price', 'time'])

    def add_order(self, order):
        self.add(order)

    def cancel_order(self, price, time):
        dummy = self.Dummy(price, time)
        self.discard(dummy)

    def best_order(self):
        return self.peekitem(0)

    def can_trade(self, price) -> bool:
        return self.peekitem(0).price >= price

    def get_someones_orders(self, token):
        return [order for key, order in self.items()
            if order.token == token]

    def get_price_qty(self):
        output = defaultdict(int)
        for _, order in self.items():
            output[order.price] += order.qty


def BidQueue2(orders=None):
     key = lambda order: (order.price, order.time)
     return OrderQueue(orders, key=key)
class BidQueue(OrderQueue):
    def __init__(self, orders):
        key = lambda order: (order.price, order.time)
        super.__init__(orders, key)



@dataclass
class Trade:
    buyer: int
    seller: int
    price: int
    qty: int

# class OrderBook:
#     def __init__(self):
#         pass

#     def add_order(self, order:Order):
#         pass

#     def execute_trade(self):
#         pass 

#     def cancel_order(self, order_id:int, token:int):
#         """Find order, Check token matched order.token, if so delete"""
#         # heap = self.bids if order_id%2 else self.offers
#         if order_id in self.offers:
#             if self.offers[order_id].token == token:
#                 self.offers.cancel_order(order_id)

#         elif order_id in self.bids:
#             if self.bids[order_id].token == token:
#                 self.bids.cancel_order(order_id)