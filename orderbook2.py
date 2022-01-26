import itertools
from sortedcontainers import SortedDict
from typing import Optional
from dataclasses import dataclass

class OrderHeap(SortedDict):
    """Actually more of a priority queue."""
    def __init__(self, orders=[], ascending=True):
        super().__init__()
        self.ascending = ascending
        self.order_ids = itertools.count(step=-1 if ascending else 1)
        self.price_qty = SortedDict()
        self.name_order = {}

        for order in orders:
            self.push(order)

    def __repr__(self):
        return f"OrderHeap(len={len(self)})" if len(self) > 20 else super().__repr__()
    
    def push(self, order):
        order.order_id = next(self.order_ids)
        self[(order.price, order.order_id)] = order
        self.price_qty[order.price] = order.qty + self.price_qty.setdefault(order.price, 0)
        self.name_order.setdefault(order.name, []).append(order)
        
    def pop(self):
        _, output = self.popitem(-1 if self.ascending else 0)
        self.price_qty[output.price] -= output.qty
        if not self.price_qty[output.price]:
            del self.price_qty[output.price]

        # this bit is slow
        self.name_order[output.name].remove(output)
        return output
    
    def can_trade(self, price):
        return bool(self and (price >= min(self) if self.ascending else price <= max(self)))

@dataclass
class Trade:
    seller: str
    buyer: str
    price: int
    qty: int

class OrderBook:
    def __init__(self):
        self.bids = OrderHeap(ascending=False)
        self.offers = OrderHeap()
        self.ledger = []
        self.positions = {}
        
    def __repr__(self):
        return f"bids: {repr(self.bids)}\noffers: {repr(self.offers)}"
        
    def do_trade(self, taker, maker):
        seller = taker.name if taker.side else maker.name
        buyer = maker.name if taker.side else taker.name
        qty = max(taker.qty, maker.qty)

        taker.qty -= qty
        maker.qty -= qty

        trade = Trade(
            seller = seller,
            buyer = buyer, 
            price = taker.price,
            qty = qty
        )

        self.ledger.append(trade)

        cash_change = taker.price * qty
        self.positions[seller]["cash"] += cash_change
        self.positions[seller]["inst"] -= qty
        self.positions[buyer]["cash"] -= cash_change
        self.positions[buyer]["inst"] += qty

    def buy_sell(self, order):
        heap = self.offers if order.side else self.bids
        
        while heap.can_trade(order.price) and order.qty > 0:
            heap_top = heap.pop()
            self.do_trade(taker=order, maker=heap_top)
            # if order.qty < heap_top.qty:
            #     self.do_trade()
            #     heap_top -= order.qty
            #     order.qty = 0
            #     heap.push(heap_top)
            # else:
            #     self.do_trade()
            #     order.qty -= heap_top.qty

            # self.do_trade(order, heap_top)
            # trade_qty = max(heap_top.qty, order.qty)
            # heap_top.qty -= trade_qty 
            # order.qty -= trade_qty 

        if order.qty > 0:
            other_heap = self.bids if order.side else self.offers
            other_heap.push(order)

@dataclass
class Order:
    price: int
    qty: int
    name: str
    side: bool
    order_id : Optional[int] = None