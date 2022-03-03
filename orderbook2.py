import itertools
from sortedcontainers import SortedDict
from typing import Optional
from dataclasses import dataclass
from collections import defaultdict

from enum import Enum

class Side(Enum):
    BUY = True
    SELL = False

class PriceQtyDict(SortedDict):
    """Like defaultdict, but sorted, for int only,
    and 0s remove themselves.
    """
    def __getitem__(self, key):
        return super().get(key, 0)
    
    def __setitem__(self, key, value):
        if value:
            super().__setitem__(key, value)
        elif key in self:
            del self[key]

class OrderHeap(SortedDict):
    """Actually more of a priority queue.
    
    Should be able to:
    Get best order
    Add order
    Delete order
    Get quantities at each price.
    Get orders for each name. 
    """
    def __init__(self, orders=[], ascending=True):
        super().__init__()
        self.ascending = ascending
        self.order_ids = itertools.count(step=1 if ascending else -1)
        self.price_qty = PriceQtyDict()
        self.name_order = defaultdict(lambda: {})#{}

        for order in orders:
            self.push(order)

    def cancel(self, order_id:int, price:int):
        order = self.pop((price, order_id))
        self.price_qty[price] -= order.qty
        self.name_order[order.name].pop((price, order_id))

    def __repr__(self):
        return f"OrderHeap(len={len(self)})" if len(self) > 20 else super().__repr__()
    
    def push(self, order):
        order.order_id = next(self.order_ids)
        self[(order.price, order.order_id)] = order
        # price_qty.add(order)
        self.price_qty[order.price] += order.qty
        # self.name_order.setdefault(order.name, []).append(order)
        self.name_order[order.name][(order.price, order.order_id)] = order
        
    def pop_top(self):
        _, output = self.popitem(0 if self.ascending else -1)
        self.price_qty[output.price] -= output.qty

        # this bit is slow???
        self.name_order[output.name].pop((output.price, output.order_id))
        return output
    
    def can_trade(self, price):
        return bool(self and (price >= min(self)[0] if self.ascending else price <= max(self)[0]))

@dataclass
class Trade:
    seller: str
    buyer: str
    price: int
    qty: int

@dataclass
class PositionChange:
    cash_change : float
    qty_change : float

class OrderBook:
    """
    Should be able to add_buy_sell_order
    Get buy/sell queues
    Get ledger
    Get positions of each party
    """
    def __init__(self):
        self.bids = OrderHeap(ascending=False)
        self.offers = OrderHeap()
        self.ledger = []
        self.positions = defaultdict(lambda: defaultdict(int))
        self.position_changes = defaultdict(lambda: [])
        
    def __repr__(self):
        return f"Bids: {repr(self.bids)}\nOffers: {repr(self.offers)}"

    def cancel_order(self, order_id:int, price:int):
        if (price, order_id) in self.bids:
            self.bids.cancel(order_id=order_id, price=price)
        elif (price, order_id) in self.offers:
            self.offers.cancel(order_id=order_id, price=price)
        
    def do_trade(self, taker, maker):
        if taker.name == maker.name:
            return # i.e. can't trade against yourself
            
        buyer = taker.name if taker.side else maker.name
        seller = maker.name if taker.side else taker.name
        qty = min(taker.qty, maker.qty)

        taker.qty -= qty
        maker.qty -= qty

        trade = Trade(
            seller = seller,
            buyer = buyer, 
            price = maker.price,
            qty = qty
        )

        self.ledger.append(trade)

        cash_change = maker.price * qty
        self.position_changes[seller].append(PositionChange(cash_change=cash_change, qty_change=-qty))
        self.position_changes[buyer].append(PositionChange(cash_change=-cash_change, qty_change=qty))

        self.positions[seller]["cash"] += cash_change
        self.positions[seller]["inst"] -= qty
        self.positions[buyer]["cash"] -= cash_change
        self.positions[buyer]["inst"] += qty

    def buy_sell(self, order):
        heap = self.offers if order.side else self.bids
        
        while heap.can_trade(order.price) and order.qty > 0:
            heap_top = heap.pop_top()
            self.do_trade(taker=order, maker=heap_top)
            if heap_top.qty > 0:
                heap.push(heap_top)

        if order.qty > 0:
            other_heap = self.bids if order.side else self.offers
            other_heap.push(order)

class Market(OrderBook):
    def __init__(self, name:str, description:str):
        self.name = name
        self.description = description
        super().__init__()

@dataclass
class Order:
    price: int
    qty: int
    name: str
    side: bool
    order_id : Optional[int] = None