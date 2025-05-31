# fastapi_price_server.py
from fastapi import FastAPI
import uvicorn
import threading
import websocket
import json

app = FastAPI()
latest_prices = {}

SYMBOLS = [
    "BTC-USD", "ETH-USD", "SOL-USD", "AVAX-USD", "LTC-USD", "OP-USD", "PEPE-USD",
    "DOGE-USD", "MATIC-USD", "INJ-USD", "SHIB-USD", "RNDR-USD", "APT-USD", "ARB-USD"
]

@app.get("/price/{symbol}")
def get_price(symbol: str):
    product_id = f"{symbol.upper()}-USD"
    return {"price": latest_prices.get(product_id)}

def on_open(ws):
    print("[🔌] WebSocket connected")
    subscribe = {
        "type": "subscribe",
        "channels": [{"name": "ticker", "product_ids": SYMBOLS}]
    }
    ws.send(json.dumps(subscribe))

def on_message(ws, message):
    try:
        data = json.loads(message)
        if data.get("type") == "ticker" and "price" in data:
            product_id = data["product_id"]
            latest_prices[product_id] = float(data["price"])
    except Exception as e:
        print(f"[WS Error] {e}")

def run_ws():
    ws = websocket.WebSocketApp(
        "wss://ws-feed.exchange.coinbase.com",
        on_open=on_open,
        on_message=on_message
    )
    ws.run_forever()

def start_websocket_thread():
    t = threading.Thread(target=run_ws)
    t.daemon = True
    t.start()

# Launch WebSocket thread when FastAPI starts
start_websocket_thread()
