from fastapi import Depends, FastAPI, Form
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse, RedirectResponse
from jinja2 import Template

import starlette.status as status

from orderbook2 import OrderBook, Order

app = FastAPI()

security = HTTPBasic()

orderbook = OrderBook()

@app.post("/cancel")
async def cancel_order(price:int=Form(...),
        order_id:int=Form(...),
        credentials: HTTPBasicCredentials = Depends(security)):
        orderbook.cancel_order(order_id, price)

        return RedirectResponse(url="/stuff", status_code=303)

@app.post("/stuff")
async def submit_order(price:int=Form(...),
        qty:int=Form(...),
        side:str=Form(...),
        credentials: HTTPBasicCredentials = Depends(security)):
    print("HELLO")
    print(side)
    side2 = side == "buy"
    order = Order(qty=qty, price=price, name=credentials.username, side=side2)
    print(order)
    orderbook.buy_sell(order)
    print(orderbook.bids)

    return RedirectResponse(url="/stuff", status_code=303)

@app.get("/stuff", response_class=HTMLResponse)
async def read_stuff(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    print("read_stuff")
    return t.render(bids=orderbook.bids.name_order[username].values(), 
                offers=orderbook.offers.name_order[username].values(), 
                username=username,
                position=orderbook.positions[username])
#     return f"""
# <head>
#     <meta charset="UTF-8">
#     <title>Sample Form</title>
# </head>
# <body>
# <p>{username}</p>
# <p>{credentials.password}</p>
# <form method="post">
#     <label>Price</label>
#     <input type="number" name="price" value="0" min="1"/>
#     <label>Qty</label>
#     <input type="number" name="qty" value="0" min="1"/>

#     <select name="side">
#     <option value="buy">Buy</option>
#     <option value="sell">Sell</option>
#     </select>

#     <button type="submit">Submit</button>
# </form>
# <p>Bids: </p>
# <p>{orderbook.bids}</p>
# <p>Offers: {orderbook.offers}</p>
# <p>Position</p>
# <p>{orderbook.positions[username]}</p>
# <p>Ledger</p>
# <p>{orderbook.ledger}</p>
# <p>Name_Order</p>
# <p>Your Bids: {orderbook.bids.name_order[username]}</p>
# <p>Your Offers: {orderbook.offers.name_order[username]}</p>
# <p>Price Qty</p>
# <p>{orderbook.bids.price_qty}</p>
# <p>{orderbook.offers.price_qty}</p>
# </body>"""


@app.get("/users/me")
def read_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    return {"username": credentials.username, "password": credentials.password}

template = """
<head>
    <meta charset="UTF-8">
    <title>Sample Form</title>
</head>
<body>
<p>Username: {{username}}</p>
<form method="post">
    <label>Price</label>
    <input type="number" name="price" value="0" min="1"/>
    <label>Qty</label>
    <input type="number" name="qty" value="0" min="1"/>

    <select name="side">
    <option value="buy">Buy</option>
    <option value="sell">Sell</option>
    </select>

    <button type="submit">Submit</button>
</form>

<p>Your Position:</p>
<p>{{position}}</p>

<p>Your Bids:</p>
<ul>
    {% for bid in bids %}
    <li>price={{bid.price}}, qty={{bid.qty}}
    <form action="/cancel" method="post">
    <input type="hidden" name="order_id" value="{{bid.order_id}}"/>
    <input type="hidden" name="price" value="{{bid.price}}"/>
    <button type="submit">Cancel</button>
    </form>
    </li>
    {% endfor %}
</ul>
<p>Your Offers:</p>
<ul>
    {% for bid in offers %}
    <li>price={{bid.price}}, qty={{bid.qty}}</li>
    {% endfor %}
</ul>
"""
t = Template(template)