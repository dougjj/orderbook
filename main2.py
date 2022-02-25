from optparse import Option
from typing import Optional
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from orderbook import OrderBook

from dataclasses import dataclass

@dataclass
class Order:
    price: float
    qty: int

app = FastAPI()

book = OrderBook()

counter = [0]

@app.get("/stuff", response_class=HTMLResponse)
async def read_stuff():
    return """
<head>
    <meta charset="UTF-8">
    <title>Sample Form</title>
</head>
<body>
<form method="post">
    <input type="number" name="price" value=""/>
    <input type="number" name="qty" value=""/>
    <input type="submit">
</form>
<p>Result: </p>
</body>"""

@app.post("/stuff", response_class=HTMLResponse)
async def more_stuff(price:int=Form(...), qty:int=Form(...)):
    book.buy(Order(price, qty))

    return await read_stuff()
    
    print("Helo")
    return book.bids.price_qty()


@app.get("/")
def reed_root():
    counter[0] += 1
    return {"counter" : counter[0]}

@app.get("/buy/")
def do_buy(price: int =0, qty: int = 0):
    book.buy(Order(price, qty))
    print("Helo")
    return book.bids.price_qty()

@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}

