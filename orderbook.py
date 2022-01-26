from sortedcontainers import SortedDict
from collections import deque

class OrderHeap(SortedDict):
    def __init__(self, orders=[], ascending=True):
        super().__init__()
        self.top = 0 if ascending else -1
        for order in orders:
            self.push(order)
        
    def push(self, order):
        self.setdefault(order.price, deque()).append(order)
    
    def pop(self):
        _, best_price_orders = self.peekitem(self.top)
        best_offer = best_price_orders.popleft()
        if not best_price_orders:
            self.popitem(self.top)
        return best_offer
    
    def price_qty(self):
        return {price : sum([order.qty for order in orders])
                   for price, orders in self.items()}

class OrderBook:
    def __init__(self):
        self.bids = OrderHeap(ascending=False)
        self.offers = OrderHeap()
        self.ledger = []
        
    def __repr__(self):
        return repr(self.bids) + repr(self.offers)
        
    def do_trade(self, *args):
        print(f"Trade: {args}")
        
    def buy(self, order):
        while self.offers and order.price >= min(self.offers) and order.qty > 0:
            best_offer = self.offers.pop()
            
            if order.qty < best_offer.qty:
                # Order filled and remainder of offer pushed
                # back on stack.
                # DO TRADE
                self.do_trade(best_offer.price, order.qty)
                best_offer.qty -= order.qty
                order.qty = 0
                self.offers.push(best_offer)
                
            else:
                # offer is consumed
                self.do_trade(best_offer.price, best_offer.qty)
                order.qty -= best_offer.qty
        if order.qty > 0:
            self.bids.push(order)
            
    def sell(self, order):
        while self.bids and order.price <= max(self.bids) and order.qty > 0:
            best_bid = self.bids.pop()
            print(f"order.qty = {order.qty}")
            
            if order.qty < best_bid.qty:
                # Order filled and remainder of offer pushed
                # back on stack.
                # DO TRADE
                self.do_trade(best_bid.price, order.qty)
                best_bid.qty -= order.qty
                order.qty = 0 
                self.bids.push(best_bid) 
            else:
                # offer is consumed
                self.do_trade(best_bid.price, best_bid.qty)
                order.qty -= best_bid.qty
                
        if order.qty > 0:
            self.offers.push(order)