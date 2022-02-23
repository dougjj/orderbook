from dataclasses import dataclass

@dataclass
class Order:
    price : int
    qty : int
    token : int
    side : bool
    order_id : int

class OrderQueue:
    def __init__(self):
        pass

    def add_order(self, order):
        pass

    def cancel_order(self):
        pass

    def best_order(self):
        pass

    def can_trade(self) -> bool:
        pass

@dataclass
class Trade:
    buyer: int
    seller: int
    price: int
    qty: int

class OrderBook:
    def __init__(self):
        pass

    def add_order(self, order:Order):
        pass

    def execute_trade(self):
        pass 

    def cancel_order(self, order_id:int, token:int):
        """Find order, Check token matched order.token, if so delete"""
        # heap = self.bids if order_id%2 else self.offers
        if order_id in self.offers:
            if self.offers[order_id].token == token:
                self.offers.cancel_order(order_id)

        elif order_id in self.bids:
            if self.bids[order_id].token == token:
                self.bids.cancel_order(order_id)