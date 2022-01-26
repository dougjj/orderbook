from fastapi import Depends, FastAPI, Form
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse

from orderbook2 import OrderBook, Order

app = FastAPI()

security = HTTPBasic()

orderbook = OrderBook()

@app.post("/stuff")
async def submit_order(price:int=Form(...),
        qty:int=Form(...),
        side:str=Form(...),
        credentials: HTTPBasicCredentials = Depends(security)):
    side2 = side == "Buy"
    order = Order(qty=qty, price=price, name=credentials.username, side=side2)
    orderbook.buy_sell(order)
    return orderbook.bids

@app.get("/stuff", response_class=HTMLResponse)
async def read_stuff(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    return f"""
<head>
    <meta charset="UTF-8">
    <title>Sample Form</title>
</head>
<body>
<p>{username}</p>
<p>{credentials.password}</p>
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
<p>Result: </p>
</body>"""



@app.get("/users/me")
def read_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    return {"username": credentials.username, "password": credentials.password}
