from fastapi import Depends, FastAPI, Form, Request, status, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse, RedirectResponse
from jinja2 import Template
from fastapi.templating import Jinja2Templates
import secrets

from orderbook2 import OrderBook, Order, Market

app = FastAPI()
templates = Jinja2Templates(directory='templates/')
security = HTTPBasic()

usernames = {'doug' : 'admin', 'abc' : 'abc'}

def get_username(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username 
    allowed_in = username in usernames and secrets.compare_digest(credentials.password, usernames[username])

    if not allowed_in:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# get admin

# orderbook = OrderBook()
orderbook = Market('XYZ', 'A market for XYZ.')
markets = {
    'XYZ' : orderbook, 
    'ABC' : Market('ABC', 'A market for ABC.')
}

# TODO: Should market be an enum? Ie
# Auto 404 if market doesn't exist?
# TODO Validate price (i.e. p>0) and order_id
@app.post("/{market}/cancel")
async def cancel_order(market:str,
        price:int=Form(...),
        order_id:int=Form(...),
        username: str = Depends(get_username)):

        if market in markets:
            ob = markets[market]
            ob.cancel_order(order_id, price)

        return RedirectResponse(url=f"/{market}/trade", status_code=303)

@app.post("/trade")
def submit_order(price:int=Form(...),
        qty:int=Form(...),
        side:str=Form(...),
        username: str = Depends(get_username)):
    side2 = side == "buy"
    order = Order(qty=qty, price=price, name=username, side=side2)
    orderbook.buy_sell(order)

    return RedirectResponse(url="/trade", status_code=303)

@app.post("/{market}/trade")
def add_order(market: str, 
        price:int=Form(...),
        qty:int=Form(...),
        side:str=Form(...),
        username: str = Depends(get_username)):
    side2 = side == "buy"
    order = Order(qty=qty, price=price, name=username, side=side2)

    markets[market].buy_sell(order)

    return RedirectResponse(url=f"/{market}/trade", status_code=303)

@app.get("/ledger")
async def get_ledger():
    return orderbook.ledger

@app.get("/{market}/trade", response_class=HTMLResponse)
def market_window(market:str, request: Request, username: str = Depends(get_username)):
    if market not in markets:
        return "Market doesn't exist."

    orderbook = markets[market]

    context = {"request" : request, 
    "position" : orderbook.positions[username],
    "bids" : orderbook.bids.name_order[username].values(),
    "offers" : orderbook.offers.name_order[username].values(),
    'username' : username,
    'ledger' : orderbook.ledger[-20:],
    'pq_bids' : reversed(orderbook.bids.price_qty.items()[-20:]),
    'pq_offers' : orderbook.offers.price_qty.items()[:20],
    'pos_change' : orderbook.position_changes[username][-20:],
    'market' : orderbook}

    return templates.TemplateResponse('trade_window.html', context=context)

@app.get("/trade", response_class=HTMLResponse)
async def trade_window(request: Request, username: str = Depends(get_username)):

    context = {"request" : request, 
    "position" : orderbook.positions[username],
    "bids" : orderbook.bids.name_order[username].values(),
    "offers" : orderbook.offers.name_order[username].values(),
    'username' : username,
    'ledger' : orderbook.ledger[-20:],
    'pq_bids' : reversed(orderbook.bids.price_qty.items()[-20:]),
    'pq_offers' : orderbook.offers.price_qty.items()[:20],
    'pos_change' : orderbook.position_changes[username][-20:],
    'market' : orderbook}

    return templates.TemplateResponse('trade_window.html', context=context)

@app.get("/users/me")
def read_current_user(username: str = Depends(get_username)):
    return {"username": username}


# @app.get("/users/me")
# def read_current_user(credentials: HTTPBasicCredentials = Depends(security)):
#     return {"username": credentials.username, "password": credentials.password}