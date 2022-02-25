from fastapi import Depends, FastAPI, Form, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse, RedirectResponse
from jinja2 import Template
from fastapi.templating import Jinja2Templates

from orderbook2 import OrderBook, Order

app = FastAPI()
templates = Jinja2Templates(directory='templates/')
security = HTTPBasic()

orderbook = OrderBook()

@app.post("/cancel")
async def cancel_order(price:int=Form(...),
        order_id:int=Form(...),
        credentials: HTTPBasicCredentials = Depends(security)):
        orderbook.cancel_order(order_id, price)

        return RedirectResponse(url="/trade", status_code=303)

@app.post("/trade")
async def submit_order(price:int=Form(...),
        qty:int=Form(...),
        side:str=Form(...),
        credentials: HTTPBasicCredentials = Depends(security)):
    side2 = side == "buy"
    order = Order(qty=qty, price=price, name=credentials.username, side=side2)
    orderbook.buy_sell(order)

    return RedirectResponse(url="/trade", status_code=303)

@app.get("/ledger")
async def get_ledger():
    return orderbook.ledger

@app.get("/trade", response_class=HTMLResponse)
async def trade_window(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username

    context = {"request" : request, 
    "position" : orderbook.positions[username],
    "bids" : orderbook.bids.name_order[username].values(),
    "offers" : orderbook.offers.name_order[username].values(),
    'username' : username,
    'ledger' : orderbook.ledger[-20:],
    'pq_bids' : reversed(orderbook.bids.price_qty.items()[-20:]),
    'pq_offers' : orderbook.offers.price_qty.items()[:20]}

    return templates.TemplateResponse('trade_window.html', context=context)

@app.get("/users/me")
def read_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    return {"username": credentials.username, "password": credentials.password}